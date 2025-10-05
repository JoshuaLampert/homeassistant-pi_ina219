"""The INA219 Power Monitor integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_I2C_ADDRESS, CONF_I2C_BUS, CONF_MAX_EXPECTED_AMPS, CONF_SHUNT_OHMS
from .sensor import INA219DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

DOMAIN = "pi_ina219"
PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up INA219 Power Monitor from a config entry."""
    _LOGGER.debug("Setting up INA219 Power Monitor integration")

    coordinator = INA219DataUpdateCoordinator(
        hass,
        i2c_bus=entry.data[CONF_I2C_BUS],
        i2c_address=entry.data[CONF_I2C_ADDRESS],
        shunt_ohms=entry.data[CONF_SHUNT_OHMS],
        max_expected_amps=entry.data[CONF_MAX_EXPECTED_AMPS],
    )

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading INA219 Power Monitor integration")

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
