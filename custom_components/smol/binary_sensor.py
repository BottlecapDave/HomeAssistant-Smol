import logging

import voluptuous as vol
from homeassistant.helpers import config_validation as cv, entity_platform

from .entities.is_on_holiday import SmolIsOnHoliday
from .api_client.account import SmolAccount
from .const import CONFIG_ACCOUNT_NAME, CONFIG_KIND, CONFIG_KIND_ACCOUNT, DATA_ACCOUNT, DATA_ACCOUNT_COORDINATOR, DATA_CLIENT, DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  config = dict(entry.data)

  if config[CONFIG_KIND] == CONFIG_KIND_ACCOUNT:
    await async_setup_default_sensors(hass, config, async_add_entities)

async def async_setup_default_sensors(hass, config, async_add_entities):
  account_name = config[CONFIG_ACCOUNT_NAME]

  client = hass.data[DOMAIN][account_name][DATA_CLIENT]

  account_result = hass.data[DOMAIN][account_name][DATA_ACCOUNT]
  account_info: SmolAccount | None = account_result.account if account_result is not None else None

  account_coordinator = hass.data[DOMAIN][account_name][DATA_ACCOUNT_COORDINATOR]

  entities = []
  if (account_info is not None):
    entities.append(SmolIsOnHoliday(hass, account_coordinator, client, account_name))

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
      "start_holiday_mode",
      vol.All(
        cv.make_entity_service_schema(
          {
            vol.Required("end_date_time"): cv.datetime
          },
          extra=vol.ALLOW_EXTRA,
        ),
      ),
      "async_start_holiday_mode"
    )

    platform.async_register_entity_service(
      "end_holiday_mode",
      vol.All(
        cv.make_entity_service_schema(
          {},
          extra=vol.ALLOW_EXTRA,
        ),
      ),
      "async_end_holiday_mode"
    )

  async_add_entities(entities, True)