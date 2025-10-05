"""Config flow for INA219 Power Monitor integration."""

from __future__ import annotations

import logging
from typing import Any

from ina219 import INA219
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_I2C_ADDRESS,
    CONF_I2C_BUS,
    CONF_MAX_EXPECTED_AMPS,
    CONF_SHUNT_OHMS,
    DEFAULT_I2C_ADDRESS,
    DEFAULT_I2C_BUS,
    DEFAULT_MAX_EXPECTED_AMPS,
    DEFAULT_SHUNT_OHMS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_I2C_BUS, default=DEFAULT_I2C_BUS): int,
        vol.Required(CONF_I2C_ADDRESS, default=DEFAULT_I2C_ADDRESS): vol.All(
            vol.Coerce(int), vol.Range(min=0x00, max=0x7F)
        ),
        vol.Required(CONF_SHUNT_OHMS, default=DEFAULT_SHUNT_OHMS): vol.All(
            vol.Coerce(float), vol.Range(min=0.001, max=1.0)
        ),
        vol.Required(
            CONF_MAX_EXPECTED_AMPS, default=DEFAULT_MAX_EXPECTED_AMPS
        ): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=10.0)),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    i2c_bus = data[CONF_I2C_BUS]
    i2c_address = data[CONF_I2C_ADDRESS]
    shunt_ohms = data[CONF_SHUNT_OHMS]

    # Test if we can initialize the INA219
    def _test_connection():
        try:
            ina = INA219(shunt_ohms, busnum=i2c_bus, address=i2c_address)
            ina.configure(ina.RANGE_16V, ina.GAIN_AUTO)
            # Try to read voltage to verify connection
            ina.voltage()
            return True
        except Exception as err:
            _LOGGER.error("Failed to connect to INA219: %s", err)
            raise CannotConnect from err

    await hass.async_add_executor_job(_test_connection)

    # Return info that you want to store in the config entry.
    return {"title": f"INA219 (0x{i2c_address:02X})"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for INA219 Power Monitor."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Create a unique ID based on I2C address
                await self.async_set_unique_id(
                    f"{user_input[CONF_I2C_BUS]}_{user_input[CONF_I2C_ADDRESS]}"
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
