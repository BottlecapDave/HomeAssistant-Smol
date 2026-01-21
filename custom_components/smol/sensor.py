import logging

from .diagnostics_entities.account_data_last_retrieved import SmolAccountDataLastRetrieved
from .entities.subscription_next_charge import SmolSubscriptionNextCharge
from .entities.subscription_quantity import SmolSubscriptionQuantity
from .entities.holiday_end_date import SmolHolidayEndDate
from .entities.is_on_holiday import SmolIsOnHoliday
from .api_client.account import SmolAccount
from .const import CONFIG_ACCOUNT_NAME, CONFIG_KIND, CONFIG_KIND_ACCOUNT, DATA_ACCOUNT, DATA_ACCOUNT_COORDINATOR, DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  config = dict(entry.data)

  if config[CONFIG_KIND] == CONFIG_KIND_ACCOUNT:
    await async_setup_default_sensors(hass, config, async_add_entities)

async def async_setup_default_sensors(hass, config, async_add_entities):
  account_name = config[CONFIG_ACCOUNT_NAME]

  account_result = hass.data[DOMAIN][account_name][DATA_ACCOUNT]
  account_info: SmolAccount | None = account_result.account if account_result is not None else None

  account_coordinator = hass.data[DOMAIN][account_name][DATA_ACCOUNT_COORDINATOR]

  entities = []
  if (account_info is not None):
    entities.append(SmolHolidayEndDate(hass, account_coordinator, account_name))
    entities.append(SmolAccountDataLastRetrieved(hass, account_coordinator, account_name))
    for subscription in account_info.subscriptions:
      entities.append(SmolSubscriptionQuantity(hass, account_coordinator, account_name, subscription))
      entities.append(SmolSubscriptionNextCharge(hass, account_coordinator, account_name, subscription))

  async_add_entities(entities, True)