# camd v2.0 - Quick Start Guide

## 🚀 What's New in v2.0

- **Focus on MI300X**: The latest AMD GPU with 192GB HBM3 memory
- **Runpod + Vultr**: Two providers with actual MI300X availability
- **Demo Mode**: Try without API keys using `--demo`
- **Provider Classes**: Easy to add new providers
- **Caching**: 5-minute cache to reduce API calls
- **Better Pricing**: Shows price per GPU for multi-GPU instances

## 📋 Installation

```bash
# Save the script
chmod +x camd.py

# Install system-wide
sudo cp camd.py /usr/local/bin/camd

# Or install for current user
mkdir -p ~/.local/bin
cp camd.py ~/.local/bin/camd
export PATH="$HOME/.local/bin:$PATH"
```

## 🔑 Setup

```bash
camd setup
```

You'll be guided through getting API keys:

### Runpod API Key
1. Go to: https://www.runpod.io/console/user/settings
2. Create API key
3. Enter when prompted

### Vultr API Key
1. Go to: https://my.vultr.com/settings/#settingsapi
2. Enable API and create key
3. Enter when prompted

## 🎮 Demo Mode (No API Keys)

Try camd without setting up API keys:

```bash
camd list --demo
```

## 💰 Find Cheapest MI300X

```bash
camd list
```

Output shows:
- All available MI300X instances sorted by price
- Price per GPU hour (important for multi-GPU setups)
- Features like spot pricing, regions, memory variants
- Comparison with NVIDIA H100 pricing

## 🚀 Deploy

Deploy the cheapest MI300X:
```bash
camd deploy mi300x
```

Deploy from specific provider:
```bash
camd deploy mi300x --provider vultr
```

## 📊 GPU Information

Get detailed MI300X specifications:
```bash
camd info mi300x
```

Shows:
- 192GB HBM3 memory (2.4x more than H100!)
- 5.3 TB/s bandwidth
- Performance specs
- Use cases
- Software support

## 💡 Key Benefits of MI300X

1. **Massive Memory**: 192GB vs H100's 80GB
2. **Cost Savings**: ~40-50% cheaper than H100
3. **Single GPU for 70B Models**: No need for complex multi-GPU setups
4. **Great Availability**: Both Runpod and Vultr have stock

## 🏷️ Current Pricing (Jan 2024)

- **Vultr**: $2.50/hr (best price!)
- **Runpod**: $2.99/hr (but 50% off with spot = $1.50/hr!)
- **H100**: ~$4.50/hr (for comparison)

## 🔥 Pro Tips

1. **Use Runpod Spot**: 50% discount brings it to $1.50/hr
2. **Vultr for Short Jobs**: Hourly billing, no commitment
3. **Cache Works**: Results cached for 5 minutes to save API calls
4. **Multi-GPU Value**: Price per GPU stays consistent

## 📝 Example Workflow

```bash
# 1. Setup (one time)
camd setup

# 2. Check prices
camd list

# 3. Deploy cheapest
camd deploy mi300x

# 4. Get instance details and start working!
```

## 🆘 Troubleshooting

**"No configuration found"**
- Run `camd setup` first
- Or use `camd list --demo` for demo mode

**"No GPUs found"**
- Check your API keys are correct
- Try `camd list --demo` to see example data

**Adding to PATH**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## 🔧 Advanced: Add New Provider

1. Copy the `ExampleProvider` class from camd.py
2. Implement `get_gpu_pricing()` and `get_available_gpus()`
3. Add to providers dict in `load_config()`
4. Add API key to .env file

## 📈 Future Providers

Watch for MI300X on:
- **Azure**: ND v5 series (coming soon)
- **OCI**: Bare metal clusters
- **TensorWave**: Specialized MI300X platform

## 💬 Support

- GitHub: https://github.com/cheapamd/camd
- Discord: https://discord.gg/cheapamd

---

**Remember**: MI300X has 2.4x more memory than H100 at 40% less cost. Perfect for large language models!