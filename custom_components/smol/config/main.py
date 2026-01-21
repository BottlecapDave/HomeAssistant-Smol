from ..const import (
  CONFIG_ACCOUNT_NAME,
  CONFIG_ACCOUNT_PASSWORD,
  CONFIG_ACCOUNT_USERNAME
)
from ..api_client import RequestException, ServerException, SmolApiClient

async def async_migrate_main_config(version: int, data: {}):
  new_data = {**data}

  return new_data

async def async_validate_main_config(data, account_ids = []):
  errors = {}

  if data[CONFIG_ACCOUNT_NAME] in account_ids:
    errors[CONFIG_ACCOUNT_NAME] = "duplicate_account_name"
    return errors
  
  if CONFIG_ACCOUNT_USERNAME not in data:
    errors[CONFIG_ACCOUNT_USERNAME] = "username_not_set"
    return errors
  
  if CONFIG_ACCOUNT_PASSWORD not in data:
    errors[CONFIG_ACCOUNT_PASSWORD] = "password_not_set"
    return errors
  
  client = SmolApiClient(data[CONFIG_ACCOUNT_USERNAME], data[CONFIG_ACCOUNT_PASSWORD])

  try:
    account_info = await client.async_get_account()
  except RequestException:
    # Treat errors as not finding the account
    account_info = None
  except ServerException:
    errors[CONFIG_ACCOUNT_USERNAME] = "server_error"
  
  if (CONFIG_ACCOUNT_USERNAME not in errors and account_info is None):
    errors[CONFIG_ACCOUNT_USERNAME] = "account_not_found"

  return errors
