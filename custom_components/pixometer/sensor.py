import logging
import asyncio
from datetime import date, datetime, timedelta

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

from . import DOMAIN, NAME
from .utils import *

_LOGGER = logging.getLogger(__name__)
_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.0%z"


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional("username", default=""): cv.string,
        vol.Optional("password", default=""): cv.string
    }
)

#TODO check if needed
MIN_TIME_BETWEEN_UPDATES = timedelta(hours=4)


async def dry_setup(hass, config_entry, async_add_devices):
    config = config_entry
    username = config.get("username")
    password = config.get("password")

    check_settings(config, hass)
    data = ComponentData(
        username,
        password,
        async_get_clientsession(hass),
        hass
    )

    await data.update()
    sensors = []
    sensor = Component(data, hass)
    sensors.append(sensor)

    async_add_devices(sensors)


async def async_setup_platform(hass, config_entry, async_add_devices, discovery_info=None):
    """Setup sensor platform for the ui"""
    _LOGGER.info("async_setup_platform " + NAME)
    await dry_setup(hass, config_entry, async_add_devices)
    return True


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor platform for the ui"""
    _LOGGER.info("async_setup_entry " + NAME)
    config = config_entry.data
    await dry_setup(hass, config, async_add_devices)
    return True

async def async_remove_entry(hass, config_entry):
    _LOGGER.info("async_remove_entry " + NAME)
    try:
        await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")
        _LOGGER.info("Successfully removed sensor from the integration")
    except ValueError:
        pass
        

class ComponentData:
    def __init__(self, username, password, client, hass):
        self._username = username
        self._password = password
        self._client = client
        self._last_update = None
        self._friendly_name = None
        self._session = ComponentSession()
        self._component = None
        self._hass = hass
        
    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def _update(self):
        _LOGGER.info("Fetching stuff for " + NAME)
        if not(self._session):
            self._session = ComponentSession()

        if self._session:
            await self._hass.async_add_executor_job(lambda: self._session.login(self._username, self._password))
            _LOGGER.info("login completed")
            self._component = await self._hass.async_add_executor_job(lambda: self._session.component())
            _LOGGER.debug(f"component data: {self._component}" + NAME)

    async def update(self):
        await self._update()
        return self._component
    
    def clear_session():
        self._session : None



class Component(Entity):
    def __init__(self, data, hass):
        self._data = data
        self._hass = hass

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._used_percentage

    async def async_update(self):
        await self._data.update()
        
        
    async def async_will_remove_from_hass(self):
        """Clean up after entity before removal."""
        _LOGGER.info("async_will_remove_from_hass " + NAME)
        self._data.clear_session()


    @property
    def icon(self) -> str:
        """Shows the correct icon for container."""
        return "mdi:check-network-outline"
        #alternative: 
        #return "mdi:wifi_tethering_error"
        
    @property
    def unique_id(self) -> str:
        """Return the name of the sensor."""
        return (
            # NAME + f"_{self._data._username.replace('-', '_')}"
            NAME
        )

    @property
    def name(self) -> str:
        return self.unique_id

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        return {
            ATTR_ATTRIBUTION: NAME,
            "last update": self._last_update
        }

    @property
    def device_info(self) -> dict:
        """I can't remember why this was needed :D"""
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": DOMAIN,
        }

    @property
    def unit(self) -> int:
        """Unit"""
        return int

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement this sensor expresses itself in."""
        return "%"

    @property
    def friendly_name(self) -> str:
        return self.unique_id
        
