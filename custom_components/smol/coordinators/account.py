import logging
from datetime import datetime, timedelta
from typing import Callable

from custom_components.smol.storage.account import async_save_cached_account
from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from homeassistant.helpers import issue_registry as ir

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DOMAIN,

  DATA_CLIENT,
  DATA_ACCOUNT,
  DATA_ACCOUNT_COORDINATOR,
  REFRESH_RATE_IN_MINUTES_ACCOUNT,
  REPAIR_ACCOUNT_NOT_FOUND,
)

from ..api_client.account import SmolAccount
from ..api_client import ApiException, AuthenticationException, SmolApiClient
from . import BaseCoordinatorResult
from ..utils.repairs import safe_repair_key

_LOGGER = logging.getLogger(__name__)

class AccountCoordinatorResult(BaseCoordinatorResult):
  account: dict

  def __init__(self, last_evaluated: datetime, request_attempts: int, account: SmolAccount, last_error: Exception | None = None):
    super().__init__(last_evaluated, request_attempts, REFRESH_RATE_IN_MINUTES_ACCOUNT, None, last_error)
    self.account = account

def raise_account_not_found(hass, name: str):
  ir.async_create_issue(
    hass,
    DOMAIN,
    safe_repair_key(REPAIR_ACCOUNT_NOT_FOUND, name),
    is_fixable=False,
    severity=ir.IssueSeverity.ERROR,
    learn_more_url="https://bottlecapdave.github.io/HomeAssistant-Smol/repairs/account_not_found",
    translation_key="account_not_found",
    translation_placeholders={ "name": name },
  )

def clear_issue(hass, key: str):
  ir.async_delete_issue(hass, DOMAIN, key)

async def async_refresh_account(
  current: datetime,
  client: SmolApiClient,
  name: str,
  previous_request: AccountCoordinatorResult,
  raise_account_not_found: Callable[[], None],
  clear_issue: Callable[[str], None]
):
  if (current >= previous_request.next_refresh):
    account_info = None
    try:
      account_info = await client.async_get_account()

      if account_info is None:
        raise_account_not_found()
      else:
        _LOGGER.debug('Account information retrieved')

        # Delete legacy issues
        clear_issue(safe_repair_key(REPAIR_ACCOUNT_NOT_FOUND, name))

        return AccountCoordinatorResult(current, 1, account_info)
    except Exception as e:
      if isinstance(e, ApiException) == False:
        raise

      if isinstance(e, AuthenticationException):
        raise_account_not_found()
      
      result = AccountCoordinatorResult(
        previous_request.last_evaluated,
        previous_request.request_attempts + 1,
        previous_request.account,
        last_error=e
      )
      
      if (result.request_attempts == 2):
        _LOGGER.warning(f'Failed to retrieve account information - using cached version. See diagnostics sensor for more information.')
      
      return result

  return previous_request

async def async_setup_account_info_coordinator(hass, name: str):
  async def async_update_account_data():
    """Fetch data from API endpoint."""
    # Only get data every half hour or if we don't have any data
    current = now()
    client: SmolApiClient = hass.data[DOMAIN][name][DATA_CLIENT]

    if DATA_ACCOUNT not in hass.data[DOMAIN][name] or hass.data[DOMAIN][name][DATA_ACCOUNT] is None:
      raise Exception("Failed to find account information")

    account_info = await async_refresh_account(
      current,
      client,
      name,
      hass.data[DOMAIN][name][DATA_ACCOUNT],
      lambda: raise_account_not_found(hass, name),
      lambda key: clear_issue(hass, key)
    )
    hass.data[DOMAIN][name][DATA_ACCOUNT] = account_info

    if account_info is not None:
      await async_save_cached_account(hass, name, account_info)
    
    return account_info

  hass.data[DOMAIN][name][DATA_ACCOUNT_COORDINATOR] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"update_account-{name}",
    update_method=async_update_account_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )
