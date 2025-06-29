#!/usr/bin/env python3
"""
camd - Check AMD hardware (CPUs & GPUs) availability across cloud providers
Enhanced to support both AMD CPUs and GPUs
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time

# Version
__version__ = "6.0.0"

# ANSI colors
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color

class AMDHardwareInfo:
    """AMD hardware specifications"""
    
    # AMD GPUs
    GPUS = {
        'MI300X': {
            'memory': '192GB HBM3',
            'memory_bandwidth': '5.3TB/s',
            'compute_units': 304,
            'use_cases': ['LLM Training', 'Inference', 'HPC'],
            'comparable_nvidia': 'H100/H200',
            'tflops_fp16': 1307.4,
            'memory_gb': 192
        },
        'MI250X': {
            'memory': '128GB HBM2e',
            'memory_bandwidth': '3.2TB/s',
            'compute_units': 220,
            'use_cases': ['HPC', 'AI Training'],
            'comparable_nvidia': 'A100',
            'tflops_fp16': 383,
            'memory_gb': 128
        }
    }
    
    # AMD CPUs
    CPUS = {
        'EPYC 7003': {
            'codename': 'Milan',
            'cores': 'Up to 64',
            'threads': 'Up to 128',
            'process': '7nm',
            'use_cases': ['General compute', 'Memory intensive', 'Databases']
        },
        'EPYC 7002': {
            'codename': 'Rome', 
            'cores': 'Up to 64',
            'threads': 'Up to 128',
            'process': '7nm',
            'use_cases': ['General compute', 'Web hosting', 'Containers']
        },
        'EPYC 9004': {
            'codename': 'Genoa',
            'cores': 'Up to 96',
            'threads': 'Up to 192',
            'process': '5nm',
            'use_cases': ['HPC', 'AI/ML', 'Enterprise']
        }
    }

class VultrProvider:
    """Vultr provider for AMD hardware"""
    def __init__(self, api_key: Optional[str] = None):
        self.name = "Vultr"
        self.api_key = api_key
        self.api_url = "https://api.vultr.com/v2"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        } if api_key else {}
        
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    def _make_api_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request to Vultr"""
        if not self.api_key:
            return None
        
        try:
            response = requests.get(
                f"{self.api_url}{endpoint}",
                headers=self.headers,
                params=params or {},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                if os.getenv('CAMD_DEBUG'):
                    print(f"Vultr API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            if os.getenv('CAMD_DEBUG'):
                print(f"Vultr API request failed: {e}")
            return None
    
    def get_amd_hardware(self) -> List[Dict]:
        """Get AMD CPUs and GPUs from Vultr"""
        if not self.api_key:
            return []
        
        plans_data = self._make_api_request("/plans")
        if not plans_data or 'plans' not in plans_data:
            return []
        
        amd_hardware = []
        
        for plan in plans_data['plans']:
            # Check for AMD GPUs
            if 'gpu_type' in plan and plan['gpu_type']:
                gpu_type = plan['gpu_type']
                if any(amd_gpu in gpu_type.upper() for amd_gpu in ['MI300X', 'MI250X', 'MI300', 'AMD']):
                    # AMD GPU found
                    gpu_model = 'MI300X' if 'MI300X' in gpu_type.upper() else \
                               'MI250X' if 'MI250X' in gpu_type.upper() else gpu_type
                    
                    amd_hardware.append({
                        'provider': self.name,
                        'hardware_type': 'GPU',
                        'model': gpu_model,
                        'instance_type': plan['id'],
                        'gpu_count': 1,
                        'gpu_vram_gb': plan.get('gpu_vram_gb', 0),
                        'vcpus': plan.get('vcpu_count', 0),
                        'memory': f"{plan.get('ram', 0) // 1024}GB",
                        'storage': f"{plan.get('disk', 0)}GB",
                        'price_per_hour': plan.get('monthly_cost', 0) / 730,
                        'price_monthly': plan.get('monthly_cost', 0),
                        'regions': plan.get('locations', []),
                        'available': len(plan.get('locations', [])) > 0,
                        'category': 'GPU Instance'
                    })
            
            # Check for AMD CPUs
            elif 'amd' in plan['id'].lower():
                # AMD CPU instance
                plan_type = plan.get('type', '')
                
                # Categorize the plan
                if 'vhp' in plan['id']:
                    category = 'High Performance AMD'
                elif 'voc' in plan['id']:
                    category = 'Optimized Cloud AMD'
                elif 'vhf' in plan['id']:
                    category = 'High Frequency AMD'
                elif 'vdc' in plan['id']:
                    category = 'Dedicated AMD'
                else:
                    category = 'Standard AMD'
                
                # Estimate CPU generation
                cpu_gen = 'EPYC 7003'  # Default to Milan
                if plan.get('vcpu_count', 0) > 64:
                    cpu_gen = 'EPYC 9004'  # Likely Genoa
                
                amd_hardware.append({
                    'provider': self.name,
                    'hardware_type': 'CPU',
                    'model': cpu_gen,
                    'instance_type': plan['id'],
                    'vcpus': plan.get('vcpu_count', 0),
                    'memory': f"{plan.get('ram', 0) / 1024:.0f}GB",
                    'storage': f"{plan.get('disk', 0)}GB",
                    'bandwidth': f"{plan.get('bandwidth_gb', 0) / 1000:.1f}TB",
                    'price_per_hour': plan.get('monthly_cost', 0) / 730,
                    'price_monthly': plan.get('monthly_cost', 0),
                    'regions': plan.get('locations', []),
                    'available': len(plan.get('locations', [])) > 0,
                    'category': category,
                    'dedicated': 'vdc' in plan['id'] or 'vbm' in plan['id']
                })
        
        return amd_hardware

class RunpodProvider:
    """RunPod provider focusing on AMD GPUs"""
    def __init__(self, api_key: Optional[str] = None):
        self.name = "RunPod"
        self.api_key = api_key
        self.graphql_url = "https://api.runpod.io/graphql"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        } if api_key else {}
        
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    def get_gpu_pricing(self) -> Dict[str, float]:
        """Get RunPod GPU pricing (defaults)"""
        return {
            'MI300X': 2.49,
            'MI250X': 1.99  # Estimate
        }
    
    def _make_graphql_query(self, query: str, variables: Dict = None) -> Optional[Dict]:
        """Make GraphQL query to RunPod API"""
        if not self.api_key:
            return None
        
        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        try:
            response = requests.post(
                self.graphql_url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "errors" in data:
                    return None
                return data.get("data")
            return None
                
        except Exception:
            return None
    
    def get_amd_hardware(self) -> List[Dict]:
        """Get AMD GPUs from RunPod"""
        if not self.api_key:
            return []
        
        gpu_types_query = """
        query GetGPUTypes {
            gpuTypes {
                id
                displayName
                memoryInGb
            }
        }
        """
        
        gpu_types_data = self._make_graphql_query(gpu_types_query)
        if not gpu_types_data or 'gpuTypes' not in gpu_types_data:
            return []
        
        amd_hardware = []
        pricing = self.get_gpu_pricing()
        
        # Find AMD GPUs
        for gpu_type in gpu_types_data['gpuTypes']:
            display_name = gpu_type.get('displayName', '')
            
            # Check for AMD GPUs
            if any(amd_gpu in display_name for amd_gpu in ['MI300X', 'MI250X', 'AMD']):
                gpu_model = 'MI300X' if 'MI300X' in display_name else \
                           'MI250X' if 'MI250X' in display_name else 'Unknown AMD'
                
                if gpu_model == 'Unknown AMD':
                    continue
                
                memory_gb = gpu_type.get('memoryInGb', 192 if gpu_model == 'MI300X' else 128)
                base_price = pricing.get(gpu_model, 2.00)
                
                # On-demand configuration
                amd_hardware.append({
                    'provider': self.name,
                    'hardware_type': 'GPU',
                    'model': gpu_model,
                    'instance_type': f'{gpu_model}-ondemand',
                    'gpu_count': 1,
                    'gpu_vram_gb': memory_gb,
                    'vcpus': 24,
                    'memory': f'{memory_gb}GB',
                    'storage': '100GB',
                    'price_per_hour': base_price,
                    'price_monthly': base_price * 730,
                    'regions': ['Global'],
                    'available': True,
                    'category': 'On-Demand GPU'
                })
                
                # Spot configuration
                amd_hardware.append({
                    'provider': self.name,
                    'hardware_type': 'GPU',
                    'model': gpu_model,
                    'instance_type': f'{gpu_model}-spot',
                    'gpu_count': 1,
                    'gpu_vram_gb': memory_gb,
                    'vcpus': 24,
                    'memory': f'{memory_gb}GB',
                    'storage': '100GB',
                    'price_per_hour': base_price * 0.5,
                    'price_monthly': base_price * 0.5 * 730,
                    'regions': ['Global (Spot)'],
                    'available': True,
                    'category': 'Spot GPU'
                })
                
                # Multi-GPU configs for MI300X
                if gpu_model == 'MI300X':
                    for count in [2, 4, 8]:
                        amd_hardware.append({
                            'provider': self.name,
                            'hardware_type': 'GPU',
                            'model': gpu_model,
                            'instance_type': f'{gpu_model}-{count}x',
                            'gpu_count': count,
                            'gpu_vram_gb': memory_gb * count,
                            'vcpus': 24 * count,
                            'memory': f'{memory_gb * count}GB',
                            'storage': f'{100 * count}GB',
                            'price_per_hour': base_price * count,
                            'price_monthly': base_price * count * 730,
                            'regions': ['Global'],
                            'available': True,
                            'category': f'{count}x GPU Cluster'
                        })
        
        return amd_hardware

class CheapAMD:
    def __init__(self):
        self.config_dir = Path.home() / '.camd'
        self.env_file = self.config_dir / '.env'
        self.cache_file = self.config_dir / 'cache.json'
        self.providers = []
        self.cache_minutes = 5
        
        # Create config directory
        self.config_dir.mkdir(exist_ok=True)
    
    def load_config(self) -> bool:
        """Load configuration from .env file"""
        if not self.env_file.exists():
            return False
        
        try:
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if value and value != 'your_key_here':
                            os.environ[key] = value
            
            # Initialize providers
            self.providers = []
            
            runpod_key = os.getenv('RUNPOD_API_KEY')
            if runpod_key:
                self.providers.append(RunpodProvider(runpod_key))
            
            vultr_key = os.getenv('VULTR_API_KEY')
            if vultr_key:
                self.providers.append(VultrProvider(vultr_key))
            
            self.cache_minutes = int(os.getenv('CAMD_CACHE_MINUTES', '5'))
            
            return len(self.providers) > 0
            
        except Exception as e:
            print(f"{Colors.RED}Error loading config: {e}{Colors.NC}")
            return False
    
    def setup(self):
        """Interactive setup wizard"""
        print(f"{Colors.GREEN}{Colors.BOLD}Welcome to camd v{__version__}!{Colors.NC}")
        print(f"{Colors.CYAN}Check AMD hardware (CPUs & GPUs) availability on cloud providers.{Colors.NC}")
        print(f"\nLet's set up your API keys.\n")
        
        # RunPod information
        print(f"{Colors.CYAN}{Colors.BOLD}RunPod{Colors.NC}")
        print(f"  {Colors.GREEN}Focus:{Colors.NC} AMD GPUs (MI300X, MI250X)")
        print(f"  {Colors.GREEN}Pricing:{Colors.NC} $2.49/hr (on-demand), ~$1.25/hr (spot)")
        print(f"  {Colors.YELLOW}Notes:{Colors.NC} Often unavailable due to high demand")
        print(f"  {Colors.MAGENTA}Get API key:{Colors.NC} {Colors.BLUE}https://www.runpod.io/console/user/settings{Colors.NC}")
        
        runpod_key = input(f"\n  RUNPOD_API_KEY (or press Enter to skip): ").strip()
        
        # Vultr information
        print(f"\n{Colors.CYAN}{Colors.BOLD}Vultr{Colors.NC}")
        print(f"  {Colors.GREEN}Focus:{Colors.NC} AMD EPYC CPUs + rare AMD GPUs")
        print(f"  {Colors.GREEN}Pricing:{Colors.NC} CPUs from $0.01/hr, GPUs vary")
        print(f"  {Colors.YELLOW}Notes:{Colors.NC} Excellent AMD CPU selection")
        print(f"  {Colors.MAGENTA}Get API key:{Colors.NC} {Colors.BLUE}https://my.vultr.com/settings/#settingsapi{Colors.NC}")
        
        vultr_key = input(f"\n  VULTR_API_KEY (or press Enter to skip): ").strip()
        
        # Build .env content
        env_content = f"""# camd (cheapamd) Configuration
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Version {__version__}
# 
# Find AMD hardware (CPUs & GPUs) across cloud providers

# RunPod API Key
"""
        
        if runpod_key:
            env_content += f"RUNPOD_API_KEY={runpod_key}\n"
        else:
            env_content += "# RUNPOD_API_KEY=your_key_here\n"
        
        env_content += "\n# Vultr API Key\n"
        
        if vultr_key:
            env_content += f"VULTR_API_KEY={vultr_key}\n"
        else:
            env_content += "# VULTR_API_KEY=your_key_here\n"
        
        env_content += "\n# Cache timeout in minutes (default: 5)\nCAMD_CACHE_MINUTES=5\n"
        env_content += "\n# Debug mode (set to 1 for verbose output)\n# CAMD_DEBUG=1\n"
        
        # Write .env file
        with open(self.env_file, 'w') as f:
            f.write(env_content)
        
        # Set secure permissions
        os.chmod(self.env_file, 0o600)
        
        print(f"\n{Colors.GREEN}✓ Configuration saved to {self.env_file}{Colors.NC}")
        
        configured = []
        if runpod_key:
            configured.append("RunPod (AMD GPUs)")
        if vultr_key:
            configured.append("Vultr (AMD CPUs)")
        
        if configured:
            print(f"\n{Colors.GREEN}Setup complete!{Colors.NC}")
            print(f"Configured: {', '.join(configured)}")
            print(f"\nCommands:")
            print(f"  {Colors.CYAN}camd list{Colors.NC}     - Show all AMD hardware")
            print(f"  {Colors.CYAN}camd list gpu{Colors.NC} - Show AMD GPUs only")
            print(f"  {Colors.CYAN}camd list cpu{Colors.NC} - Show AMD CPUs only")
        else:
            print(f"\n{Colors.YELLOW}No API keys configured.{Colors.NC}")
            print(f"Edit {self.env_file} to add your keys later.")
    
    def get_all_hardware(self, use_cache: bool = True) -> List[Dict]:
        """Get all AMD hardware from providers"""
        
        # Check cache
        if use_cache and self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    cache_time = datetime.fromisoformat(cache_data['timestamp'])
                    if datetime.now() - cache_time < timedelta(minutes=self.cache_minutes):
                        return cache_data['hardware']
            except:
                pass
        
        # Fetch from providers
        all_hardware = []
        for provider in self.providers:
            try:
                hardware = provider.get_amd_hardware()
                all_hardware.extend(hardware)
            except Exception as e:
                if os.getenv('CAMD_DEBUG'):
                    print(f"Error fetching from {provider.name}: {e}")
        
        # Cache results
        if all_hardware:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'hardware': all_hardware
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)
        
        return all_hardware
    
    def list_hardware(self, hardware_type: Optional[str] = None):
        """List AMD hardware with optional filtering"""
        
        if not self.load_config():
            print(f"{Colors.YELLOW}No configuration found. Run 'camd setup' first.{Colors.NC}")
            return
        
        print(f"{Colors.MAGENTA}{Colors.BOLD}💰 camd v{__version__} - Checking AMD hardware availability...{Colors.NC}\n")
        
        # Get all hardware
        hardware = self.get_all_hardware()
        
        if not hardware:
            print(f"{Colors.RED}No AMD hardware found.{Colors.NC}")
            return
        
        # Apply filter
        if hardware_type:
            hardware = [h for h in hardware if h['hardware_type'].lower() == hardware_type.lower()]
        
        if not hardware:
            print(f"{Colors.RED}No {hardware_type} instances found.{Colors.NC}")
            return
        
        # Sort by price
        hardware.sort(key=lambda x: x['price_per_hour'])
        
        # Separate GPUs and CPUs
        gpus = [h for h in hardware if h['hardware_type'] == 'GPU']
        cpus = [h for h in hardware if h['hardware_type'] == 'CPU']
        
        # Show GPUs
        if gpus:
            print(f"{Colors.CYAN}{Colors.BOLD}━━━ AMD GPU Instances ━━━{Colors.NC}")
            
            # Show MI300X specs
            if 'MI300X' in [g['model'] for g in gpus]:
                specs = AMDHardwareInfo.GPUS['MI300X']
                print(f"MI300X: {specs['memory']} | {specs['memory_bandwidth']} | {specs['tflops_fp16']} TFLOPS")
                print()
            
            print(f"{'💵 $/hr':<10} {'Provider':<12} {'Model':<10} {'Count':<6} {'VRAM':<10} {'Type':<20} {'Available':<10}")
            print("─" * 90)
            
            for gpu in gpus:
                price_str = f"${gpu['price_per_hour']:.2f}"
                available = "✓" if gpu['available'] else "✗"
                available_color = Colors.GREEN if gpu['available'] else Colors.RED
                
                print(f"{price_str:<10} {gpu['provider']:<12} "
                      f"{gpu['model']:<10} {gpu.get('gpu_count', 1):<6} "
                      f"{gpu.get('gpu_vram_gb', 'N/A')}GB".ljust(10) + " "
                      f"{gpu['instance_type']:<20} "
                      f"{available_color}{available:<10}{Colors.NC}")
        
        # Show CPUs
        if cpus:
            print(f"\n{Colors.CYAN}{Colors.BOLD}━━━ AMD CPU Instances ━━━{Colors.NC}")
            print(f"AMD EPYC processors - Industry leading performance")
            print()
            
            print(f"{'💵 $/hr':<10} {'Provider':<12} {'Type':<20} {'vCPUs':<8} {'RAM':<10} {'Category':<25}")
            print("─" * 90)
            
            # Show top 20 cheapest
            for cpu in cpus[:20]:
                price_str = f"${cpu['price_per_hour']:.2f}"
                
                print(f"{price_str:<10} {cpu['provider']:<12} "
                      f"{cpu['instance_type']:<20} {cpu['vcpus']:<8} "
                      f"{cpu['memory']:<10} {cpu['category']:<25}")
            
            if len(cpus) > 20:
                print(f"\n... and {len(cpus) - 20} more AMD CPU instances")
        
        # Summary
        print(f"\n{Colors.CYAN}Summary:{Colors.NC}")
        print(f"  Total AMD hardware: {len(hardware)} configurations")
        if gpus:
            print(f"  AMD GPUs: {len(gpus)} configurations")
            gpu_models = {}
            for g in gpus:
                gpu_models[g['model']] = gpu_models.get(g['model'], 0) + 1
            for model, count in gpu_models.items():
                print(f"    • {model}: {count} options")
        
        if cpus:
            print(f"  AMD CPUs: {len(cpus)} configurations")
            # Price ranges
            cpu_prices = [c['price_per_hour'] for c in cpus]
            print(f"    • Price range: ${min(cpu_prices):.2f} - ${max(cpu_prices):.2f}/hr")
            print(f"    • Median: ${sorted(cpu_prices)[len(cpu_prices)//2]:.2f}/hr")
    
    def show_help(self):
        """Show help message"""
        print(f"{Colors.MAGENTA}{Colors.BOLD}camd - AMD Hardware on Cloud Providers{Colors.NC}")
        print(f"Version {__version__} - Now with CPU support!\n")
        
        print(f"{Colors.CYAN}About:{Colors.NC}")
        print(f"  Find AMD CPUs and GPUs across cloud providers.")
        print(f"  Supports MI300X GPUs and EPYC CPUs.")
        
        print(f"\n{Colors.CYAN}Commands:{Colors.NC}")
        print(f"  {Colors.BOLD}setup{Colors.NC}                    Configure API keys")
        print(f"  {Colors.BOLD}list{Colors.NC}                     List all AMD hardware")
        print(f"  {Colors.BOLD}list gpu{Colors.NC}                 List AMD GPUs only")
        print(f"  {Colors.BOLD}list cpu{Colors.NC}                 List AMD CPUs only")
        print(f"  {Colors.BOLD}help{Colors.NC}                     Show this help")
        
        print(f"\n{Colors.CYAN}Examples:{Colors.NC}")
        print(f"  camd setup              # Configure providers")
        print(f"  camd list               # Show all AMD hardware")
        print(f"  camd list gpu           # AMD GPUs only")
        print(f"  camd list cpu           # AMD CPUs only")


    def setup(self):
        """Interactive setup wizard"""
        print(f"{Colors.GREEN}{Colors.BOLD}Welcome to camd v{__version__}!{Colors.NC}")
        print(f"{Colors.CYAN}Check AMD hardware (CPUs & GPUs) availability on cloud providers.{Colors.NC}")
        print(f"\nLet's set up your API keys.\n")
        
        # RunPod information
        print(f"{Colors.CYAN}{Colors.BOLD}RunPod{Colors.NC}")
        print(f"  {Colors.GREEN}Focus:{Colors.NC} AMD GPUs (MI300X, MI250X)")
        print(f"  {Colors.GREEN}Pricing:{Colors.NC} $2.49/hr (on-demand), ~$1.25/hr (spot)")
        print(f"  {Colors.YELLOW}Notes:{Colors.NC} Often unavailable due to high demand")
        print(f"  {Colors.MAGENTA}Get API key:{Colors.NC} {Colors.BLUE}https://www.runpod.io/console/user/settings{Colors.NC}")
        
        runpod_key = input(f"\n  RUNPOD_API_KEY (or press Enter to skip): ").strip()
        
        # Vultr information
        print(f"\n{Colors.CYAN}{Colors.BOLD}Vultr{Colors.NC}")
        print(f"  {Colors.GREEN}Focus:{Colors.NC} AMD EPYC CPUs + rare AMD GPUs")
        print(f"  {Colors.GREEN}Pricing:{Colors.NC} CPUs from $0.01/hr, GPUs vary")
        print(f"  {Colors.YELLOW}Notes:{Colors.NC} Excellent AMD CPU selection")
        print(f"  {Colors.MAGENTA}Get API key:{Colors.NC} {Colors.BLUE}https://my.vultr.com/settings/#settingsapi{Colors.NC}")
        
        vultr_key = input(f"\n  VULTR_API_KEY (or press Enter to skip): ").strip()
        
        # Build .env content
        env_content = f"""# camd (cheapamd) Configuration
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Version {__version__}
# 
# Find AMD hardware (CPUs & GPUs) across cloud providers

# RunPod API Key
"""
        
        if runpod_key:
            env_content += f"RUNPOD_API_KEY={runpod_key}\n"
        else:
            env_content += "# RUNPOD_API_KEY=your_key_here\n"
        
        env_content += "\n# Vultr API Key\n"
        
        if vultr_key:
            env_content += f"VULTR_API_KEY={vultr_key}\n"
        else:
            env_content += "# VULTR_API_KEY=your_key_here\n"
        
        env_content += "\n# Cache timeout in minutes (default: 5)\nCAMD_CACHE_MINUTES=5\n"
        env_content += "\n# Debug mode (set to 1 for verbose output)\n# CAMD_DEBUG=1\n"
        
        # Write .env file
        with open(self.env_file, 'w') as f:
            f.write(env_content)
        
        # Set secure permissions
        os.chmod(self.env_file, 0o600)
        
        print(f"\n{Colors.GREEN}✓ Configuration saved to {self.env_file}{Colors.NC}")
        
        configured = []
        if runpod_key:
            configured.append("RunPod (AMD GPUs)")
        if vultr_key:
            configured.append("Vultr (AMD CPUs)")
        
        if configured:
            print(f"\n{Colors.GREEN}Setup complete!{Colors.NC}")
            print(f"Configured: {', '.join(configured)}")
            print(f"\nCommands:")
            print(f"  {Colors.CYAN}camd list{Colors.NC}     - Show all AMD hardware")
            print(f"  {Colors.CYAN}camd list gpu{Colors.NC} - Show AMD GPUs only")
            print(f"  {Colors.CYAN}camd list cpu{Colors.NC} - Show AMD CPUs only")
        else:
            print(f"\n{Colors.YELLOW}No API keys configured.{Colors.NC}")
            print(f"Edit {self.env_file} to add your keys later.")


def main():
    """Main entry point"""
    camd = CheapAMD()
    
    if len(sys.argv) < 2:
        camd.show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'setup':
        camd.setup()
    
    elif command == 'list':
        filter_type = None
        if len(sys.argv) > 2:
            filter_type = sys.argv[2].upper()
            if filter_type not in ['CPU', 'GPU']:
                filter_type = None
        
        camd.list_hardware(hardware_type=filter_type)
    
    elif command in ['help', '-h', '--help']:
        camd.show_help()
    
    else:
        print(f"{Colors.RED}Unknown command: {command}{Colors.NC}")
        print("Run 'camd help' for usage")
        sys.exit(1)


if __name__ == '__main__':
    main()