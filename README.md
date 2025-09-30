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

### I2C Permission Issues

If you get permission errors, add the Home Assistant user to the i2c group:

```bash
sudo usermod -a -G i2c homeassistant
```

Then restart Home Assistant.

### Cannot Connect Error

- Verify I2C is enabled: `sudo raspi-config`
- Check the sensor is detected: `sudo i2cdetect -y 1`
- Verify wiring connections (VCC, GND, SDA, SCL)
- Check I2C address matches your configuration

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
