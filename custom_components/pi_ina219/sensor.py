"""Sensor platform for INA219 Power Monitor."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from ina219 import INA219, DeviceRangeError

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up INA219 sensor from a config entry."""
    coordinator: INA219DataUpdateCoordinator = config_entry.runtime_data

    entities = [
        INA219VoltageSensor(coordinator, config_entry),
        INA219CurrentSensor(coordinator, config_entry),
        INA219PowerSensor(coordinator, config_entry),
    ]

    async_add_entities(entities)


class INA219DataUpdateCoordinator(DataUpdateCoordinator[dict[str, float]]):
    """Class to manage fetching INA219 data."""

    def __init__(
        self,
        hass: HomeAssistant,
        i2c_bus: int,
        i2c_address: int,
        shunt_ohms: float,
        max_expected_amps: float,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="INA219 Power Monitor",
            update_interval=SCAN_INTERVAL,
        )
        self.i2c_bus = i2c_bus
        self.i2c_address = i2c_address
        self.shunt_ohms = shunt_ohms
        self.max_expected_amps = max_expected_amps
        self._ina = None

    def _init_sensor(self) -> None:
        """Initialize the INA219 sensor."""
        if self._ina is None:
            self._ina = INA219(
                self.shunt_ohms,
                busnum=self.i2c_bus,
                address=self.i2c_address,
            )
            self._ina.configure(self._ina.RANGE_16V, self._ina.GAIN_AUTO)

    async def _async_update_data(self) -> dict[str, float]:
        """Fetch data from INA219."""
        return await self.hass.async_add_executor_job(self._update_data)

    def _update_data(self) -> dict[str, float]:
        """Fetch data from INA219 (runs in executor)."""
        try:
            self._init_sensor()

            voltage = self._ina.voltage()
            current = self._ina.current() / 1000  # Convert mA to A
            power = self._ina.power() / 1000  # Convert mW to W

            return {
                "voltage": voltage,
                "current": current,
                "power": power,
            }
        except DeviceRangeError as err:
            raise UpdateFailed(f"Current out of device range: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Error communicating with INA219: {err}") from err


class INA219SensorBase(CoordinatorEntity[INA219DataUpdateCoordinator], SensorEntity):
    """Base class for INA219 sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: INA219DataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{config_entry.entry_id}")},
            name="INA219 Power Monitor",
            manufacturer="Texas Instruments",
            model="INA219",
        )


class INA219VoltageSensor(INA219SensorBase):
    """Sensor for INA219 voltage measurement."""

    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_name = "Voltage"

    def __init__(
        self,
        coordinator: INA219DataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the voltage sensor."""
        super().__init__(coordinator, config_entry)
        self._attr_unique_id = f"{config_entry.entry_id}_voltage"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("voltage")


class INA219CurrentSensor(INA219SensorBase):
    """Sensor for INA219 current measurement."""

    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_name = "Current"

    def __init__(
        self,
        coordinator: INA219DataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the current sensor."""
        super().__init__(coordinator, config_entry)
        self._attr_unique_id = f"{config_entry.entry_id}_current"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("current")


class INA219PowerSensor(INA219SensorBase):
    """Sensor for INA219 power measurement."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_name = "Power"

    def __init__(
        self,
        coordinator: INA219DataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the power sensor."""
        super().__init__(coordinator, config_entry)
        self._attr_unique_id = f"{config_entry.entry_id}_power"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("power")
