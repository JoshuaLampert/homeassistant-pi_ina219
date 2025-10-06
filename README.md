# INA219 Power Monitor for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License: MIT](https://img.shields.io/badge/License-MIT-success.svg)](https://opensource.org/licenses/MIT)

Home Assistant integration to measure current, voltage, and power with an [INA219 sensor](https://www.ti.com/lit/ds/symlink/ina219.pdf) from Texas Instruments using the Python library [pi-ina219](https://github.com/chrisb2/pi_ina219).

## Features

- Measures voltage (V)
- Measures current (A)
- Measures power (W)
- Easy configuration through the Home Assistant UI
- Automatically creates sensors
- Automatic updates every 30 seconds

## Hardware Requirements

- Raspberry Pi or similar device running Home Assistant
- INA219 current/power monitor module
- I2C connection enabled on your device

Especially, this means no ESP is required because the INA219 is directly wired to the Raspberry Pi running Home Assistant.

## Installation

### HACS (Recommended)

1. Add this repository to HACS as a custom repository:
   - Go to HACS
   - Click the three dots in the top right corner
   - Select "Custom repositories"
   - Add `https://github.com/JoshuaLampert/homeassistant-pi_ina219` as an Integration
   - Click "Add"

2. Install the integration:
   - Search for "INA219 Power Monitor" in HACS
   - Click "Download"
   - Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/pi_ina219` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

### Preparation

Home Assistant OS requires I2C to be enabled through the system configuration. There are several methods:
The easiest and most reliable method is to use the dedicated add-on:

1. Install the **"HassOS I2C Configurator"** add-on:
   - In the add-on store add the repository: `https://github.com/adamoutler/HassOSConfigurator`
   - Install the add-on

2. Start the add-on - it will automatically configure I2C. Check the logs to see if it was successful.

3. **Important:** Reboot your Raspberry Pi twice (full reboot, not just Home Assistant restart):
   - Go to Developer Tools → Restart → Advanced Options → Reboot system
   - Wait for it to come back online, then reboot again
   - This ensures I2C drivers are properly loaded

4. Verify I2C is available using the **Terminal & SSH** or **Advanced SSH & Web Terminal** add-on:
   ```bash
   ls -l /dev/i2c*
   ```
   You should see devices like `/dev/i2c-0`, `/dev/i2c-1`, etc. Note: In a normal setup on a Raspberry Pi not
   running Home Assistant OS, we would verify the INA219 is detected at bus number 1 by running
   ```
   i2cdetect -y 1
   ```
   This command returns the I2C Address if it is detected properly. However, on Home Assistant OS, this would normally
   give a permission error. But if you disable the protection-mode in the SSH add-on, you can execute `i2cdetect` in a
   docker container like this:
   ```sh
   ➜  ~ docker exec -it homeassistant bash -c "apk add i2c-tools && i2cdetect -y 1"
   fetch https://dl-cdn.alpinelinux.org/alpine/v3.21/main/aarch64/APKINDEX.tar.gz
   fetch https://dl-cdn.alpinelinux.org/alpine/v3.21/community/aarch64/APKINDEX.tar.gz
   (1/1) Installing i2c-tools (4.3-r3)
   Executing busybox-1.37.0-r12.trigger
   0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
   00:                         -- -- -- -- -- -- -- --
   10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
   20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
   30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
   40: 40 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
   50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
   60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
   70: -- -- -- -- -- -- -- --
   ```
   This tells you that at bus number `1` a device at address `0x40` is detected.

For more information and troubleshooting, see the [forum thread](https://community.home-assistant.io/t/add-on-hassos-i2c-configurator/264167).

### Adding the Integration

Add the integration through the Home Assistant UI:
  - Go to Settings -> Devices & Services
  - Click "+ Add Integration"
  - Search for "INA219 Power Monitor"
  - Enter your configuration:
    - **I2C Bus Number**: Usually `1` for Raspberry Pi
    - **I2C Address**: Usually `0x40` (64 in decimal), note that the slider accepts decimal values, so you have to translate the hex value to decimal
    - **Shunt Resistor Value**: Typically `0.1` ohms (check your module specifications)
    - **Maximum Expected Current**: Maximum current you expect to measure (e.g., `3.2` amps)

## Configuration Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| I2C Bus Number | The I2C bus number | 1 | - |
| I2C Address | The I2C address of the INA219 | 0x40 | 0x00-0x7F (0-127 in decimal) |
| Shunt Resistor Value | The value of the shunt resistor in ohms | 0.1 | 0.001-1.0 |
| Maximum Expected Current | Maximum current in amps | 3.2 | 0.1-10.0 |

## Sensors

The integration creates three sensors:

- **Voltage** - Bus voltage in volts (V)
- **Current** - Current in amperes (A)
- **Power** - Power in watts (W)

## Troubleshooting

### I2C Not Enabled on Home Assistant OS

If you're running Home Assistant OS and getting "Cannot Connect" errors:

**Check if I2C is enabled:**
  - Install **Terminal & SSH** or **Advanced SSH & Web Terminal** add-on
  - Open the terminal and check for I2C device: `ls -l /dev/i2c*`
  - If no devices are listed, I2C is not enabled

### Integration Still Fails After Enabling I2C (Home Assistant OS)

If you've enabled I2C (you see `/dev/i2c-*` devices) but the integration still shows "Cannot Connect":

1. **Check detailed error logs:**
   - Go to Settings → System → Logs
   - Look for errors mentioning "INA219" or "pi_ina219"
   - Common errors:
     - `Permission denied`: I2C device permissions issue (rare on HA OS)
     - `[Errno 5] I/O error`: Sensor not responding - check hardware, address, or bus number
     - `Remote I/O error` or `No such device`: Sensor not detected on bus
     - `OSError: [Errno 16]`: Device address conflict or sensor not properly connected

2. **Verify hardware connections:**
   - VCC → 3.3V or 5V (check your INA219 module specifications)
   - GND → GND
   - SDA → GPIO 2 (Pin 3) on Raspberry Pi
   - SCL → GPIO 3 (Pin 5) on Raspberry Pi
   - Ensure connections are secure

3. **Verify the sensor is working:**
   - The default address is 0x40 (decimal 64)
   - Some INA219 modules have address selection jumpers - verify they're set correctly
   - Try a different I2C address in the integration config (0x41, 0x44, or 0x45)

4. **Check if another process is using the sensor:**
   - Restart Home Assistant after changing I2C configuration
   - Make sure no other integrations are trying to use the same I2C address

### Inaccurate Readings

- Verify the shunt resistor value matches your hardware
- Ensure the maximum expected current is set correctly
- Check that your power supply is stable

## Similar projects

- [INA219 DC Current Sensor in ESP](https://esphome.io/components/sensor/ina219/): Also creates current, voltage, and power sensors, but via ESPHome, i.e. an additional ESP device is required.
- [INA219 UPS hat integration](https://github.com/odya/hass-ina219-ups-hat): Home Assistant integration to monitor any INA219 based UPS hat
- [HomeAssistant INA219 sensor](https://github.com/ochorocho/ina_sensor)

## Credits

- Based on the [pi-ina219](https://github.com/chrisb2/pi_ina219) Python library by Chris Borrill
- INA219 chip by Texas Instruments

## Disclaimer

Please note that large parts of this integration are written by GitHub Copilot, see [this PR](https://github.com/JoshuaLampert/homeassistant-pi_ina219/pull/1).
I have checked the implementation and tested the integration though. However, I do not extend any warranty. Use at your own risk!

## License and contributing

This project is under the MIT License (see [License](https://github.com/JoshuaLampert/homeassistant-pi_ina219/blob/main/LICENSE)).
I am pleased to accept contributions from everyone, preferably in the form of a PR.

## Support

For issues, questions, or contributions, please [open an issue](https://github.com/JoshuaLampert/homeassistant-pi_ina219/issues)
or [create a pull request](https://github.com/JoshuaLampert/homeassistant-pi_ina219/pulls).
