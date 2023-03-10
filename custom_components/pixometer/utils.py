import json
import logging
import pprint
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import List
import requests
from pydantic import BaseModel

import voluptuous as vol
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.0%z"

def check_settings(config, hass):
    if not any(config.get(i) for i in ["username"]):
        _LOGGER.debug("username was not set")
    else:
        return True
    if not config.get("password"):
        _LOGGER.debug("password was not set")
    else:
        return True

    raise vol.Invalid("Missing settings to setup the sensor.")


class ComponentSession(object):
    def __init__(self):
        # self.s = client
        self.s = requests.Session()
        self.s.headers["User-Agent"] = "Python/3"
        self.s.headers["Content-Type"] = "application/json"
        self._bearer_token = None

    def login(self, username, password):
        header = {"Content-Type": "application/json"}
        response = self.s.post("https://pixometer.io/api/v1/access-token/",data='{"username": "'+username+'","password": "'+password+'"}',headers=header,timeout=10)
        _LOGGER.debug("post result status code: " + str(response.status_code))
        _LOGGER.debug("post result response: " + str(response.text))
        assert response.status_code == 200
        response_json = response.json()
        self._bearer_token = "Bearer " + response_json.get("access_token")

    def meterlist(self):
        response = self.s.get(
            "https://pixometer.io/api/v1/meters/",
            headers={
                "Authorization": self._bearer_token,
            },
            timeout=10,
        )
        assert response.status_code == 200
        return response.json()

    def meter_readings(self, meter_id):
        response = self.s.get("https://pixometer.io/api/v1/readings/?meter_id=" + str(meter_id) + "&o=-created",
            headers={
                "Authorization": self._bearer_token,
            },
            timeout=10,
        )
        _LOGGER.debug(" result status code: " + str(response.status_code))
        _LOGGER.debug(" result " + response.text)
        assert response.status_code == 200
        return response.json()
