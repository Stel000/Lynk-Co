
"""Support for the Xiaomi device tracking."""
import logging
import datetime
import time

from homeassistant.components.device_tracker import SOURCE_TYPE_GPS
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.const import (
    ATTR_BATTERY_LEVEL,
    ATTR_GPS_ACCURACY,
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
)
from homeassistant.core import callback
from homeassistant.helpers import device_registry
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.helpers.entity import Entity

from .const import (
    DOMAIN,
    COORDINATOR,
    SIGNAL_STATE_UPDATED
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistantType, config_entry, async_add_entities):
    """Configure a dispatcher connection based on a config entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    devices = []
    for i in range(len(coordinator.data)):
        devices.append(LynkCOEntity(hass, coordinator, i))
        _LOGGER.debug("device is : %s", i)
    async_add_entities(devices, True)

class LynkCOEntity(TrackerEntity, RestoreEntity, Entity):
    """Represent a tracked device."""

    def __init__(self, hass, coordinator, vin) -> None:
        """Set up Geofency entity."""
        self._hass = hass
        self._vin = vin
        self.coordinator = coordinator  
        self._unique_id = coordinator.data[vin]["vehicleStatus"]['configuration']['vin']
        self._name = coordinator.data[vin]["plateNo"]
        self._icon = "mdi:car"
        self.sw_version = '001'

    async def async_update(self):
        """Update Colorfulclouds entity."""   
        _LOGGER.debug("async_update")
        await self.coordinator.async_request_refresh()
    async def async_added_to_hass(self):
        """Subscribe for update from the hub"""

        _LOGGER.debug("device_tracker_unique_id: %s", self._unique_id)

        async def async_update_state():
            """Update sensor state."""
            await self.async_update_ha_state(True)

        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    @property
    def device_state_attributes(self):
        """Return device specific attributes."""
        updateTime = self.coordinator.data[self._vin]["vehicleStatus"]['updateTime']
        attrs = {
            "last_update": updateTime,
            "data": self.coordinator.data[self._vin]["vehicleStatus"],
            "vin": self._unique_id
        }
        return attrs

    @property
    def latitude(self):
        """Return latitude value of the device."""
        return (self.coordinator.data[self._vin]['vehicleStatus']["basicVehicleStatus"]['position']['latitude'])/3600000

    @property
    def longitude(self):
        """Return longitude value of the device."""
        return (self.coordinator.data[self._vin]['vehicleStatus']["basicVehicleStatus"]['position']['longitude'])/3600000


    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique ID."""
        return self._unique_id
    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self._unique_id)},
            "name": self._name,
            "manufacturer": "Lynk&Co",
            "entry_type": "device",
            "sw_version": self.sw_version,
            "model": self._name
        }
    @property
    def should_poll(self):
        """Return the polling requirement of the entity."""
        return False

    @property
    def source_type(self):
        """Return the source type, eg gps or router, of the device."""
        return SOURCE_TYPE_GPS

        

