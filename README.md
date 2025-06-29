# camd - Find AMD Hardware on Cloud ☁️

<div align="center">

[![Version](https://img.shields.io/badge/version-6.0.0-blue.svg)](https://github.com/modelturnedgeek/CheaperNvidia)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.6+-yellow.svg)](https://www.python.org)

**The easiest way to find AMD GPUs and CPUs across cloud providers**

[Installation](#-installation) •
[Quick Start](#-quick-start) •
[Features](#-features) •
[Providers](#-supported-providers) •
[Hardware](#-supported-hardware) •
[Roadmap](#-roadmap)

</div>

---

## 🚀 Overview

`camd` (cheapamd) is a command-line tool that helps you find available AMD hardware across cloud providers. With the massive 192GB memory of MI300X GPUs and powerful EPYC CPUs, AMD offers compelling alternatives to NVIDIA hardware.

### Why AMD?

- **MI300X GPU**: 192GB HBM3 memory (2.4x more than H100!)
- **High Performance**: Excellent compute capabilities
- **EPYC CPUs**: Best price/performance for CPU workloads
- **Availability**: Often easier to find than scarce H100s

## ✨ Features

### Current Capabilities (v6.0.0)

- **🔍 Multi-Provider Search**: Vultr and RunPod support
- **💎 AMD GPU Discovery**: Find MI300X (192GB) and MI250X (128GB)
- **💻 AMD CPU Discovery**: All EPYC variants (Milan, Rome, Genoa)
- **💰 Price Comparison**: Sort by hourly cost
- **🏷️ Spot Pricing**: 50% discounts on RunPod
- **📦 Multi-GPU Configs**: 1x, 2x, 4x, 8x GPU clusters
- **⚡ Smart Caching**: 5-minute cache to reduce API calls
- **🎨 Beautiful CLI**: Color-coded output with emojis
- **🔐 Secure**: API keys stored locally with 600 permissions

## 📦 Installation

```bash
# Download the script
curl -O https://raw.githubusercontent.com/modelturnedgeek/CheaperNvidia/main/camd.py
chmod +x camd.py

# Install system-wide
sudo cp camd.py /usr/local/bin/camd

# Or install for current user
mkdir -p ~/.local/bin
cp camd.py ~/.local/bin/camd
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Requirements
- Python 3.6+
- `requests` library (`pip install requests`)

## 🚀 Quick Start

### 1. Setup (One-time)
```bash
camd setup
```

You'll be guided to get API keys from:
- **RunPod**: https://www.runpod.io/console/user/settings
- **Vultr**: https://my.vultr.com/settings/#settingsapi

### 2. Find AMD Hardware
```bash
# List all AMD hardware (GPUs + CPUs)
camd list

# List only AMD GPUs
camd list gpu

# List only AMD CPUs  
camd list cpu
```

## 📊 Sample Output

```
💰 camd v6.0.0 - Checking AMD hardware availability...

━━━ AMD GPU Instances ━━━
MI300X: 192GB HBM3 | 5.3TB/s | 1307.4 TFLOPS

💵 $/hr    Provider     Model      Count  VRAM       Type                 Available
─────────────────────────────────────────────────────────────────────────────────
$1.25      RunPod       MI300X     1      192GB      MI300X-spot          ✓
$2.49      RunPod       MI300X     1      192GB      MI300X-ondemand      ✓
$2.50      Vultr        MI300X     1      192GB      gpu-mi300x-1         ✓
$5.00      Vultr        MI300X     2      384GB      gpu-mi300x-2         ✓

━━━ AMD CPU Instances ━━━
AMD EPYC processors - Industry leading performance

💵 $/hr    Provider     Type                 vCPUs    RAM        Category
─────────────────────────────────────────────────────────────────────────────────
$0.01      Vultr        vhf-1c-1gb-amd       1        1GB        High Frequency AMD
$0.01      Vultr        vhp-1c-1gb-amd       1        1GB        High Performance AMD
$0.02      Vultr        vhf-1c-2gb-amd       1        2GB        High Frequency AMD
...
```

## 🏢 Supported Providers

### Current Providers

| Provider | AMD GPUs | AMD CPUs | API Status | Notes |
|----------|----------|----------|------------|--------|
| **RunPod** | ✅ MI300X, MI250X | ❌ | Stable | Best for GPU workloads, spot pricing available |
| **Vultr** | 🔄 Limited | ✅ EPYC | Stable | Excellent CPU selection, some GPU availability |

### Provider Details

#### RunPod
- **Strengths**: GPU-focused, spot instances (50% off), global availability
- **GPUs**: MI300X ($2.49/hr), MI250X ($1.99/hr estimated)
- **Features**: Multi-GPU clusters, persistent storage, Jupyter support

#### Vultr
- **Strengths**: Wide CPU selection, hourly billing, 25+ locations
- **CPUs**: EPYC 7003 (Milan), 7002 (Rome), 9004 (Genoa)
- **Types**: High Performance (vhp), Optimized Cloud (voc), High Frequency (vhf)



## 💡 Use Cases

### Perfect for MI300X (192GB)
- **70B+ LLMs**: Run Llama-70B on a single GPU!
- **RAG Systems**: Massive context windows
- **Multi-modal AI**: Image + text models
- **Scientific Computing**: Large memory requirements

### Perfect for AMD CPUs
- **Web Hosting**: Better price/performance than Intel
- **Databases**: High memory bandwidth
- **Containers**: Excellent multi-threading
- **CI/CD**: Cost-effective build servers

## 🛠️ Advanced Usage

### Environment Variables
```bash
# API Keys
export RUNPOD_API_KEY='your-key'
export VULTR_API_KEY='your-key'

# Cache timeout (minutes)
export CAMD_CACHE_MINUTES=5

# Debug mode
export CAMD_DEBUG=1
```

### Configuration File
```bash
# Location: ~/.camd/.env
RUNPOD_API_KEY=your_runpod_key
VULTR_API_KEY=your_vultr_key
CAMD_CACHE_MINUTES=5
```

## 🤝 Contributing

We welcome contributions! Here's how to add a new provider:

1. Create a new provider class inheriting from base
2. Implement `get_amd_hardware()` method
3. Add to provider initialization in `load_config()`
4. Submit PR with example output

### Development Setup
```bash
git clone https://github.com/modelturnedgeek/CheaperNvidia
cd CheaperNvidia
pip install requests  # Only dependency
python camd.py setup
```

## 🔧 Troubleshooting

### Common Issues

**"No configuration found"**
```bash
camd setup  # Run setup first
```

**"No AMD hardware found"**
- Check API keys are valid
- Ensure you have network connectivity
- Try with debug mode: `CAMD_DEBUG=1 camd list`

**API Rate Limits**
- Results are cached for 5 minutes
- Adjust with `CAMD_CACHE_MINUTES`

## 📚 Resources

- [AMD Instinct MI300X](https://www.amd.com/en/products/accelerators/instinct/mi300/mi300x.html)
- [AMD EPYC Processors](https://www.amd.com/en/processors/epyc)
- [RunPod Documentation](https://docs.runpod.io)
- [Vultr API Docs](https://www.vultr.com/api/)

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- AMD for making competitive hardware
- Cloud providers offering AMD instances
- The open-source community

---

<div align="center">

**Built with ❤️ for the AMD community**

[Report Bug](https://github.com/modelturnedgeek/CheaperNvidia/issues) •
[Request Feature](https://github.com/modelturnedgeek/CheaperNvidia/issues)

</div>