import voluptuous as vol
import logging

from homeassistant.config_entries import (ConfigFlow)

from .config.main import async_validate_main_config
from .const import (
  CONFIG_ACCOUNT_NAME,
  CONFIG_ACCOUNT_PASSWORD,
  CONFIG_ACCOUNT_USERNAME,
  CONFIG_KIND,
  CONFIG_KIND_ACCOUNT,
  CONFIG_VERSION,
  DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

def get_account_names(hass):
    account_names: list[str] = []
    for entry in hass.config_entries.async_entries(DOMAIN, include_ignore=False):
      if CONFIG_KIND in entry.data and entry.data[CONFIG_KIND] == CONFIG_KIND_ACCOUNT:
        account_name = entry.data[CONFIG_ACCOUNT_NAME]
        account_names.append(account_name)

    return account_names

class SmolConfigFlow(ConfigFlow, domain=DOMAIN): 
  """Config flow."""

  VERSION = CONFIG_VERSION

  _target_entity_id = None
  
  def __setup_account_schema__(self, include_account_name = True):
    schema = {
      vol.Required(CONFIG_ACCOUNT_NAME): str,
      vol.Required(CONFIG_ACCOUNT_USERNAME): str,
      vol.Required(CONFIG_ACCOUNT_PASSWORD): str,
    }

    if (include_account_name == False):
      del schema[CONFIG_ACCOUNT_NAME]

    return vol.Schema(schema)
  
  async def async_step_account(self, user_input):
    """Setup the initial account based on the provided user input"""
    account_names = get_account_names(self.hass)
    errors = await async_validate_main_config(user_input, account_names) if user_input is not None else {}

    if len(errors) < 1 and user_input is not None:
      user_input[CONFIG_KIND] = CONFIG_KIND_ACCOUNT
      return self.async_create_entry(
        title=user_input[CONFIG_ACCOUNT_NAME], 
        data=user_input
      )

    return self.async_show_form(
      step_id="account",
      data_schema=self.add_suggested_values_to_schema(
        self.__setup_account_schema__(),
        user_input if user_input is not None else {}
      ),
      errors=errors
    )
  
  async def async_step_reconfigure_account(self, user_input):
    """Setup the initial account based on the provided user input"""
    config = dict()
    config.update(self._get_reconfigure_entry().data)

    if user_input is not None:
      config.update(user_input)

    account_ids = []
    errors = await async_validate_main_config(config, account_ids)

    if len(errors) < 1 and user_input is not None:
      return self.async_update_reload_and_abort(
        self._get_reconfigure_entry(),
        data_updates=config,
      )

    return self.async_show_form(
      step_id="reconfigure_account",
      data_schema=self.add_suggested_values_to_schema(
        self.__setup_account_schema__(False),
        config
      ),
      errors=errors
    )

  async def async_step_user(self, user_input):
    """Setup based on user config"""

    if user_input is not None:
      if CONFIG_KIND in user_input:
        if user_input[CONFIG_KIND] == CONFIG_KIND_ACCOUNT:
          return await self.async_step_account(user_input)
        
      return self.async_abort(reason="unexpected_entry")

    return self.async_show_form(
      step_id="account",
      data_schema=self.__setup_account_schema__(),
    )
  
  async def async_step_reconfigure(self, user_input):
    """Manage the options for the custom component."""
    kind = self._get_reconfigure_entry().data[CONFIG_KIND]

    if (kind == CONFIG_KIND_ACCOUNT):
      return await self.async_step_reconfigure_account(user_input)

    return self.async_abort(reason="reconfigure_not_supported")