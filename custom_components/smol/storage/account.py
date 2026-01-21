import logging
from ..api_client.account import SmolAccount
from homeassistant.helpers import storage

_LOGGER = logging.getLogger(__name__)

async def async_load_cached_account(hass, account_name: str):
  store = storage.Store(hass, "1", f"smol/{account_name}_account.json")

  try:
    data = await store.async_load()
    if data is not None:
      _LOGGER.debug(f"Loaded cached account data for {account_name}")
    return SmolAccount.model_validate(data)
  except:
    return None
  
async def async_save_cached_account(hass, account_name: str, account_data: SmolAccount):
  if account_data is not None:
    store = storage.Store(hass, "1", f"smol/{account_name}_account.json")
    await store.async_save(account_data.dict())
    _LOGGER.debug(f"Saved account data for ({account_name})")