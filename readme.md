# SA_AE108 Scent Marketing Diffuser API

Python API for controlling SA_AE108 Scent Marketing fragrance diffusers via Bluetooth Low Energy (BLE).

This project provides a command-line interface and Python library for programmatically controlling commercial scent diffusers, enabling home automation, scheduling, and integration with other systems.

## Features

✅ **Simple Control** - Turn pump on/off with precise timing (0-4000ms)  
✅ **Device Information** - Query PCB and equipment versions  
✅ **Fast Connection** - Optimized for quick BLE scanning and connection  
✅ **Automation Ready** - Command-line interface for scripting and cron jobs  
✅ **Silent Mode** - Quiet operation for background automation  
✅ **Error Handling** - Automatic pump shutdown on errors  

## Hardware Compatibility

**Tested with:**
- **Model:** SA_AE108_0000B984
- **Manufacturer:** Scent Marketing
- **Type:** Commercial fragrance diffuser
- **Connection:** Bluetooth Low Energy (BLE)

**May work with similar models** - If you test with other Scent Marketing diffusers, please contribute your findings!

## Requirements

### Hardware
- Scent Marketing SA_AE108 diffuser
- Computer with Bluetooth Low Energy support

### Software
- Python 3.7+
- SimplePyBLE library

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/lglasbergen/Scent-Marketing-API
cd sa-ae108-diffuser-api
```

### 2. Install Dependencies
```bash
pip3 install simplepyble
```

**On some systems you may need:**
```bash
pip3 install simplepyble --break-system-packages
```

### 3. Configure Your Device

Edit `scent_marketing_api.py` and update the device constants:
```python
TARGET_NAME = "SA_AE108_0000B984"  # Your diffuser's name
TARGET_MAC  = "0B03C9C2-9BFC-5E07-4C68-65E6A594E503"  # Your diffuser's MAC address
```

**To find your device details:**
1. Use a BLE scanner app (nRF Connect, LightBlue, etc.)
2. Look for devices starting with "SA_AE108"
3. Note the full name and MAC address

## Usage

### Basic Commands
```bash
# Run pump for 2 seconds (default)
python3 scent_marketing_api.py

# Run pump for 3 seconds (3000ms)
python3 scent_marketing_api.py -d 3000

# Run pump for 500 milliseconds
python3 scent_marketing_api.py -d 500

# Turn pump on and immediately off
python3 scent_marketing_api.py -d 0

# Get device version information
python3 scent_marketing_api.py --versions

# Run silently (no output)
python3 scent_marketing_api.py -d 2000 --quiet
```

### Command-Line Options
```
Options:
  -h, --help            Show help message
  -v, --versions        Get device version information only
  -d, --duration MS     Pump duration in milliseconds (0-4000, default: 2000)
  -q, --quiet           Quiet mode - minimal output
```

### Examples

**Quick burst (500ms):**
```bash
python3 scent_marketing_api.py -d 500
```

**Long run (4 seconds):**
```bash
python3 scent_marketing_api.py -d 4000
```

**Check versions:**
```bash
python3 scent_marketing_api.py --versions
```
Output:
```
============================================================
DEVICE VERSION INFORMATION
============================================================
PCB Version: V2.00
Equipment Version: V3.4
============================================================
```

**Silent operation (for cron jobs):**
```bash
python3 scent_marketing_api.py -d 1500 --quiet
```

## Reverse Engineering Notes

This API was created through BLE packet capture and analysis using:
- **Nordic nRF52840** BLE Sniffer
- **Wireshark** with BLE dissectors
- **Python/Scapy** for packet analysis
- **SimplePyBLE** for device control

### Commands Discovered

| Command | Hex | Description |
|---------|-----|-------------|
| Login | `8f38383838` | Authenticate with device (causes beep) |
| Pump ON | `03110000173b7f0a0a000000000000` | Start pump at full intensity |
| Pump OFF | `03010000173b7f0a0a000000000000` | Stop pump |
| Get PCB Version | `86503d11` | Query PCB version (V2.00) |
| Get Equipment Version | `88d02119` | Query equipment version (V3.4) |

### BLE Characteristics
```
Service UUID:        0000fff0-0000-1000-8000-00805f9b34fb
Characteristic UUID: 0000fff6-0000-1000-8000-00805f9b34fb
Properties:          Read, Write, Notify
```

### Version Response Format

Responses contain ASCII-encoded version strings:
- PCB Version: `V2.00` (returned from 0x86503d11 command)
- Equipment Version: `V3.4` (returned from 0x88d02119 command)

## License

MIT License - see LICENSE file for details

## Disclaimer

⚠️ **Important:**
- This is an **unofficial** reverse-engineered API
- **Not affiliated** with or endorsed by Scent Marketing
- Use at your own risk
- You cannot connect this script and the Scent Marketing App at the same time to the device
- This was reversed engineering used the iPhone App


## Changelog

### v1.0.0 (2024-12-06)
- Initial release
- Basic pump control (on/off)
- Duration control (0-4000ms)
- Version query support (PCB and Equipment versions)
- Command-line interface
- Quiet mode for automation

---

**Star ⭐ this repo if you find it useful!**
