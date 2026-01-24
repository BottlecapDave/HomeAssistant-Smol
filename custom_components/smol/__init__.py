from datetime import timedelta
import logging

from homeassistant.const import (
    EVENT_HOMEASSISTANT_STOP
)
from homeassistant.helpers import (
  issue_registry as ir
)
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.util.dt import (utcnow)

from .api_client import ApiException, AuthenticationException, SmolApiClient
from .config.main import async_migrate_main_config
from .const import CONFIG_ACCOUNT_NAME, CONFIG_ACCOUNT_PASSWORD, CONFIG_ACCOUNT_USERNAME, CONFIG_KIND, CONFIG_KIND_ACCOUNT, CONFIG_VERSION, DATA_ACCOUNT, DATA_CLIENT, DOMAIN, REFRESH_RATE_IN_MINUTES_ACCOUNT, REPAIR_ACCOUNT_NOT_FOUND
from .coordinators.account import AccountCoordinatorResult, async_setup_account_info_coordinator
from .utils.repairs import safe_repair_key
from .storage.account import async_load_cached_account, async_save_cached_account

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)

ACCOUNT_PLATFORMS = ["sensor", "binary_sensor"]

async def async_migrate_entry(hass, config_entry):
  """Migrate old entry."""
  if (config_entry.version < CONFIG_VERSION):
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    new_data = dict(config_entry.data)
    title = config_entry.title

    if CONFIG_KIND in new_data and new_data[CONFIG_KIND] == CONFIG_KIND_ACCOUNT:
      new_data = await async_migrate_main_config(config_entry.version, new_data, hass.config_entries.async_entries)
    
    hass.config_entries.async_update_entry(config_entry, title=title, data=new_data, options={}, version=CONFIG_VERSION)

    _LOGGER.debug("Migration to version %s successful", config_entry.version)

  return True

async def options_update_listener(hass, entry):
  """Handle options update."""
  await hass.config_entries.async_reload(entry.entry_id)

  if entry.data[CONFIG_KIND] == CONFIG_KIND_ACCOUNT:
    account_name = entry.data[CONFIG_ACCOUNT_NAME]

    # If the main account has been reloaded, then reload all other entries to make sure they're referencing
    # the correct references (e.g. rate coordinators)
    child_entries = hass.config_entries.async_entries(DOMAIN, include_ignore=False)
    for child_entry in child_entries:
      child_entry_config = dict(child_entry.data)

      if child_entry_config[CONFIG_KIND] != CONFIG_KIND_ACCOUNT and child_entry_config[CONFIG_ACCOUNT_NAME] == account_name:
        await hass.config_entries.async_reload(child_entry.entry_id)

async def async_unload_entry(hass, entry):
    """Unload a config entry."""

    unload_ok = False
    if entry.data[CONFIG_KIND] == CONFIG_KIND_ACCOUNT:
      unload_ok = await hass.config_entries.async_unload_platforms(entry, ACCOUNT_PLATFORMS)
      if unload_ok:
        account_name = entry.data[CONFIG_ACCOUNT_NAME]
        await _async_close_client(hass, account_name)
        hass.data[DOMAIN].pop(account_name)

    return unload_ok

async def _async_close_client(hass, account_name: str):
  if account_name in hass.data[DOMAIN]:
    if DATA_CLIENT in hass.data[DOMAIN][account_name]:
      _LOGGER.debug('Closing client...')
      client: SmolApiClient = hass.data[DOMAIN][account_name][DATA_CLIENT]
      await client.async_close()
      _LOGGER.debug('Client closed.')

async def async_setup_entry(hass, entry):
  """This is called from the config flow."""
  hass.data.setdefault(DOMAIN, {})

  config = dict(entry.data)

  account_name = config[CONFIG_ACCOUNT_NAME]
  hass.data[DOMAIN].setdefault(account_name, {})

  if config[CONFIG_KIND] == CONFIG_KIND_ACCOUNT:
    await async_setup_account(hass, account_name, config)
    await hass.config_entries.async_forward_entry_setups(entry, ACCOUNT_PLATFORMS)

    async def async_close_connection(_) -> None:
      """Close client."""
      await _async_close_client(hass, account_name)

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, async_close_connection)
    )

    # If the main account has been reloaded, then reload all other entries to make sure they're referencing
    # the correct references (e.g. rate coordinators)
    child_entries = hass.config_entries.async_entries(DOMAIN, include_ignore=False)
    for child_entry in child_entries:
      child_entry_config = dict(child_entry.data)

      if child_entry_config[CONFIG_KIND] != CONFIG_KIND_ACCOUNT and child_entry_config[CONFIG_ACCOUNT_NAME] == account_name:
        await hass.config_entries.async_reload(child_entry.entry_id)
  
  entry.async_on_unload(entry.add_update_listener(options_update_listener))

  return True

async def async_setup_account(hass, account_name, config):
  await async_setup_account_info_coordinator(hass, account_name)
    
  await _async_close_client(hass, account_name)
  client = SmolApiClient(config[CONFIG_ACCOUNT_USERNAME], config[CONFIG_ACCOUNT_PASSWORD])
  hass.data[DOMAIN][account_name][DATA_CLIENT] = client
  
  # Delete any issues that may have been previously raised
  ir.async_delete_issue(hass, DOMAIN, safe_repair_key(REPAIR_ACCOUNT_NOT_FOUND, account_name))

  is_cached_account = False
  try:
    account_info = await client.async_get_account()
    if (account_info is None):
      raise ConfigEntryNotReady(f"Failed to retrieve account information")
    await async_save_cached_account(hass, account_name, account_info)
  except Exception as e:
    if isinstance(e, ApiException) == False:
      raise

    if isinstance(e, AuthenticationException):
      ir.async_create_issue(
        hass,
        DOMAIN,
        safe_repair_key(REPAIR_ACCOUNT_NOT_FOUND, account_name),
        is_fixable=False,
        severity=ir.IssueSeverity.ERROR,
        translation_key="account_not_found",
        translation_placeholders={ "name": account_name },
      )
      raise ConfigEntryNotReady(f"Failed to retrieve account information: {e}")
    else:
      is_cached_account = True
      account_info = await async_load_cached_account(hass, account_name)
      if (account_info is None):
        raise ConfigEntryNotReady(f"Failed to retrieve account information: {e}")
      else:
        _LOGGER.warning(f"Using cached account information for {account_name} during startup. This data will be updated automatically when available.")
  
  hass.data[DOMAIN][account_name][DATA_ACCOUNT] = AccountCoordinatorResult(utcnow() + timedelta(minutes=REFRESH_RATE_IN_MINUTES_ACCOUNT if not is_cached_account else 0), 1, account_info)