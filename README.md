# INA219 Power Monitor for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Home Assistant integration to measure current, voltage, and power with an INA219 sensor using the Python library `pi-ina219`.

## Features

- Measures voltage (V)
- Measures current (A)
- Measures power (W)
- Easy configuration through the Home Assistant UI
- Automatic updates every 30 seconds
- HACS compatible

## Hardware Requirements

- Raspberry Pi or similar device running Home Assistant
- INA219 current/power monitor module
- I2C connection enabled on your device

## Installation

### HACS (Recommended)

1. Add this repository to HACS as a custom repository:
   - Go to HACS -> Integrations
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

### For Standard Raspberry Pi OS

1. Enable I2C on your Raspberry Pi:
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options -> I2C -> Enable
   ```

2. Verify your INA219 is detected:
   ```bash
   sudo i2cdetect -y 1
   ```
   You should see your device address (typically 0x40)

### For Home Assistant OS

Home Assistant OS requires I2C to be enabled through the system configuration. There are several methods:

#### Method 1: Using HassOS I2C Configurator Add-on (Recommended)

The easiest and most reliable method is to use the dedicated add-on:

1. Install the **"HassOS I2C Configurator"** add-on:
   - Add the repository: `https://github.com/adamoutler/HassOSConfigurator`
   - Or search for "HassOS I2C Configurator" in the Community Add-on Store
   - Install the add-on

2. Start the add-on - it will automatically configure I2C

3. Restart Home Assistant: Go to Settings → System → Restart

4. Verify I2C is available using the **Terminal & SSH** or **Advanced SSH & Web Terminal** add-on:
   ```bash
   ls -l /dev/i2c*
   i2cdetect -y 1
   ```
   You should see your device address (typically 0x40)

**Note:** This add-on is specifically designed for Home Assistant OS and handles all the configuration automatically, including dealing with the correct config.txt path for your HA OS version.

#### Method 2: Using configuration.yaml (May work on some HA OS versions)

1. Add the following to your `configuration.yaml`:
   ```yaml
   # Enable I2C
   hardware:
   ```

2. Restart Home Assistant

3. Verify I2C is available using the **Terminal & SSH** or **Advanced SSH & Web Terminal** add-on:
   ```bash
   ls -l /dev/i2c*
   ```

#### Method 3: Editing config.txt manually (Advanced - if other methods don't work)

1. Install the **File editor** add-on from the Add-on Store

2. In the File editor, navigate to the `/config` directory

3. Create or edit a file called `config.txt` in the root of your config directory with the following content:
   ```
   dtparam=i2c_arm=on
   ```
   
4. Alternatively, use **Terminal & SSH** or **Advanced SSH & Web Terminal** add-on:
   ```bash
   # Check if config.txt exists in various possible locations
   ls -l /boot/config.txt /mnt/boot/config.txt /mnt/data/supervisor/config.txt
   
   # Edit the file that exists (path may vary by HA OS version)
   # If using /boot/config.txt:
   echo "dtparam=i2c_arm=on" >> /boot/config.txt
   
   # Reboot
   ha host reboot
   ```

5. After reboot, verify I2C is available:
   ```bash
   ls -l /dev/i2c*
   i2cdetect -y 1
   ```
   You should see your device address (typically 0x40)

### Adding the Integration

3. Add the integration through the Home Assistant UI:
   - Go to Settings -> Devices & Services
   - Click "+ Add Integration"
   - Search for "INA219 Power Monitor"
   - Enter your configuration:
     - **I2C Bus Number**: Usually `1` for Raspberry Pi
     - **I2C Address**: Usually `0x40` (64 in decimal) - check with `i2cdetect`
     - **Shunt Resistor Value**: Typically `0.1` ohms (check your module specifications)
     - **Maximum Expected Current**: Maximum current you expect to measure (e.g., `3.2` amps)

## Configuration Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| I2C Bus Number | The I2C bus number | 1 | - |
| I2C Address | The I2C address of the INA219 | 0x40 | 0x00-0x7F |
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

1. **Check if I2C is enabled:**
   - Install **Terminal & SSH** or **Advanced SSH & Web Terminal** add-on
   - Open the terminal and check for I2C device: `ls -l /dev/i2c*`
   - If no devices are listed, I2C is not enabled

2. **Enable I2C on Home Assistant OS:**
   
   **Method 1 (Recommended):** Use the **HassOS I2C Configurator** add-on:
   - Install from: `https://github.com/adamoutler/HassOSConfigurator`
   - Start the add-on
   - Restart Home Assistant
   - The add-on handles everything automatically
   
   **Method 2:** Add to `configuration.yaml`:
   ```yaml
   hardware:
   ```
   Then restart Home Assistant.
   
   **Method 3:** Edit config.txt manually (Advanced):
   - The location of `config.txt` varies by HA OS version
   - Try these locations: `/boot/config.txt`, `/mnt/boot/config.txt`, or `/mnt/data/supervisor/config.txt`
   - Use the Terminal add-on to check which exists: `ls -l /boot/config.txt /mnt/boot/config.txt`
   - Edit the file that exists and add: `dtparam=i2c_arm=on`
   - Reboot: `ha host reboot`

3. **Verify the sensor is detected:**
   ```bash
   i2cdetect -y 1
   ```
   You should see your device address (typically 0x40 or 40)

### I2C Permission Issues (Standard Raspberry Pi OS)

If you get permission errors on standard Raspberry Pi OS, add the Home Assistant user to the i2c group:

```bash
sudo usermod -a -G i2c homeassistant
```

Then restart Home Assistant.

### Cannot Connect Error

- **Home Assistant OS**: Verify I2C is enabled (see above)
- **Raspberry Pi OS**: Verify I2C is enabled: `sudo raspi-config`
- Check the sensor is detected: `sudo i2cdetect -y 1` (or `i2cdetect -y 1` on HA OS)
- Verify wiring connections:
  - VCC → 3.3V or 5V (check your module specs)
  - GND → GND
  - SDA → GPIO 2 (Pin 3)
  - SCL → GPIO 3 (Pin 5)
- Check I2C address matches your configuration (default: 0x40)
- Some INA219 modules have address selection jumpers - verify they're set correctly

### Inaccurate Readings

- Verify the shunt resistor value matches your hardware
- Ensure the maximum expected current is set correctly
- Check that your power supply is stable

## Example Automation

Monitor power consumption and send a notification:

```yaml
automation:
  - alias: "High Power Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.ina219_power_monitor_power
        above: 10
    action:
      - service: notify.notify
        data:
          message: "Power consumption is above 10W!"
```

## Development

This integration uses the [pi-ina219](https://github.com/chrisb2/pi_ina219) Python library.

## Credits

- Based on the [pi-ina219](https://github.com/chrisb2/pi_ina219) library by Chris Borrill
- INA219 chip by Texas Instruments

## License

This project is under the MIT License.

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/JoshuaLampert/homeassistant-pi_ina219/issues).
