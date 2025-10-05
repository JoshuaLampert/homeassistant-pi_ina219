"""Constants for the INA219 Power Monitor integration."""

DOMAIN = "pi_ina219"

# Configuration constants
CONF_I2C_BUS = "i2c_bus"
CONF_I2C_ADDRESS = "i2c_address"
CONF_SHUNT_OHMS = "shunt_ohms"
CONF_MAX_EXPECTED_AMPS = "max_expected_amps"

# Default values
DEFAULT_I2C_BUS = 1
DEFAULT_I2C_ADDRESS = 0x40
DEFAULT_SHUNT_OHMS = 0.1
DEFAULT_MAX_EXPECTED_AMPS = 3.2
