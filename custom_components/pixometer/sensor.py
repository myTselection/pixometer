import logging
import asyncio
from datetime import date, datetime, timedelta

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.util import Throttle
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass

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
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=2)


async def dry_setup(hass, config_entry, async_add_devices):
    config = config_entry
    username = config.get("username")
    password = config.get("password")

    check_settings(config, hass)
    data = ComponentData(
        username,
        password,
        hass
    )

    # meter_list = await data.initiate()
    meter_list = await data._init_meter_list()
    
    for meter_details in meter_list.get("results"):
        sensors = []
        meter_reading = await data.update_meter_readings(meter_details.get("meter_id"))
        sensor = Component(data, meter_details, meter_reading, hass)
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
    def __init__(self, username, password, hass):
        self._username = username
        self._password = password
        self._last_update = None
        self._friendly_name = None
        self._session = ComponentSession()
        self._meter_list = None
        self._hass = hass
        self._meter_readings = dict()
        
    # async def initiate(self):
    #     _LOGGER.info("Fetching stuff for " + NAME)
    #     if not(self._session):
    #         self._session = ComponentSession()

    #     if self._session:
    #         await self._hass.async_add_executor_job(lambda: self._session.login(self._username, self._password))
    #         _LOGGER.debug("login completed " + NAME)
    #         self._meter_list = None
    #         self._meter_list = await self._hass.async_add_executor_job(lambda: self._session.meterlist())
    #         _LOGGER.debug("meter list retrieved " + NAME)    
    #         assert self._meter_list is not None
    #     return self._meter_list
        
        
    # @Throttle(MIN_TIME_BETWEEN_UPDATES)
    # async def _update(self, meter_id):
    #     if not(self._session):
    #         self._session = ComponentSession()

    #     if self._session:
    #         await self._hass.async_add_executor_job(lambda: self._session.login(self._username, self._password))
    #         meter_readings = await self._hass.async_add_executor_job(lambda: self._session.meter_readings(meter_id))
    #         _LOGGER.debug(f"updated meter readings for {NAME} - meter id: {meter_id}") 
    #         assert meter_readings is not None
    #         self._meter_readings[meter_id] = meter_readings.get("results")[0]
        
    # async def update(self, meter_id):
    #     await self._update(meter_id)
    #     _LOGGER.debug(f"updated meter readings for {NAME} - meter id: {meter_id} - result: {self._meter_readings.get(meter_id)}") 
    #     return self._meter_readings.get(meter_id)
    
    async def _init_meter_list(self):
        _LOGGER.info("Forced updated for " + NAME)
        if not(self._session):
            self._session = ComponentSession()

        if self._session:
            await self._hass.async_add_executor_job(lambda: self._session.login(self._username, self._password))
            _LOGGER.debug("login completed " + NAME)
            self._meter_list = None
            self._meter_list = await self._hass.async_add_executor_job(lambda: self._session.meterlist())
            _LOGGER.debug("meter list retrieved " + NAME)    
            assert self._meter_list is not None
            return self._meter_list


    # same as update, but without throttle to make sure init is always executed
    async def _forced_update(self):
        _LOGGER.info("Forced updated for " + NAME)
        if not(self._session):
            self._session = ComponentSession()

        if self._session:
            await self._hass.async_add_executor_job(lambda: self._session.login(self._username, self._password))
            _LOGGER.debug("login completed " + NAME)
            
            for meter_details in self._meter_list.get("results"):
                await self.update_meter_readings(meter_details.get("meter_id"))

    
    async def update_meter_readings(self, meter_id):
        meter_readings = await self._hass.async_add_executor_job(lambda: self._session.meter_readings(meter_id))
        _LOGGER.info(f"init meter readings for {NAME} - meter id: {meter_id}") 
        assert meter_readings is not None
        self._meter_readings[meter_id] = meter_readings.get("results")[0]
        return meter_readings.get("results")[0]
                
    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def _update(self):
        await self._forced_update()

    async def update(self):
        await self._update()
    
    def clear_session(self):
        self._session : None

class Component(Entity):
    def __init__(self, data, meter_details, meter_reading, hass):
        self._data = data
        self._meter_details = meter_details
        self._meter_reading = meter_reading
        self._meter_id = self._meter_details.get("meter_id")
        self._hass = hass

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._meter_reading.get("value")

    async def async_update(self):
        await self._data.update()
        self._meter_reading = self._data._meter_readings.get(self._meter_id)
        
        
    async def async_will_remove_from_hass(self):
        """Clean up after entity before removal."""
        _LOGGER.info("async_will_remove_from_hass " + NAME)


    @property
    def icon(self) -> str:
        """Return icon based on physical_medium."""
        icon = "mdi:check-network-outline"
        if self._meter_details.get("physical_medium") == "electricity":
            icon = "mdi:flash"
        if self._meter_details.get("physical_medium") == "gas":
            icon = "mdi:radiator"
        if self._meter_details.get("physical_medium") == "water":
            icon = "mdi:water-pump"
        return icon
        
    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._meter_details.get('resource_id')


    @property
    def has_entity_name(self) -> bool:
        return True

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        return {
            ATTR_ATTRIBUTION: NAME,
            "last update": self._meter_reading.get("reading_date"),
            "physical_medium": self._meter_details.get("physical_medium"),
            "physical_unit": self._meter_details.get("physical_unit").replace("^3","³").replace("^2","²"),
            "meter_id": self._meter_details.get("meter_id"),
            "description": self._meter_details.get("description"),
            "image": self._meter_reading.get("image_meta").get("image")
        }

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        name = self._meter_details.get("label")
        if name == "" or name is None:
            name = f"{NAME} {self._meter_details.get('location_in_building').replace('-', '_')}"
        return DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name=name,
            manufacturer="pixolus GmbH",
            suggested_area=self._meter_details.get("location_in_building"),
            configuration_url=f"https://pixometer.io/portal/#/meters/{self._meter_details.get('resource_id')}/edit",
        )

    @property
    def unit(self) -> int:
        """Unit"""
        return int

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement this sensor expresses itself in."""
        return self._meter_details.get("physical_unit").replace("^3","³").replace("^2","²")

    @property
    def friendly_name(self) -> str:
        return self.unique_id
        
    @property
    def device_class(self) -> str:
        device_class = None
        if self._meter_details.get("physical_medium") == "electricity":
            device_class = SensorDeviceClass.ENERGY
        if self._meter_details.get("physical_medium") == "gas":
            device_class = SensorDeviceClass.GAS
        if self._meter_details.get("physical_medium") == "water":
            device_class = SensorDeviceClass.WATER
        return device_class
    
    @property
    def state_class(self) -> str:
        state_class = None
        if self.device_class == SensorDeviceClass.GAS or self.device_class == SensorDeviceClass.WATER:
            # Gas and Water meters can only increase. A lower value means the meter has been replaced.
            state_class = SensorStateClass.TOTAL_INCREASING
        if self.device_class == SensorDeviceClass.ENERGY:
            # Recent electricity meters can only increase. But pixometer is used to read old meters, and
            # old meters can decrease e.g. when supplying current to the grid.
            state_class = SensorStateClass.TOTAL
        return state_class
