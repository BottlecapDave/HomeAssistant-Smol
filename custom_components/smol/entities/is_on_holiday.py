import logging

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity
)
from homeassistant.helpers.restore_state import RestoreEntity

from ..utils.attributes import dict_to_typed_dict
from ..api_client.account import SmolAccount
from ..coordinators.account import AccountCoordinatorResult

_LOGGER = logging.getLogger(__name__)

class SmolIsOnHoliday(CoordinatorEntity, BinarySensorEntity, RestoreEntity):
  """Sensor for determining if the account is on holiday."""
  
  _unrecorded_attributes = frozenset({"data_last_retrieved"})

  def __init__(self, hass: HomeAssistant, coordinator, account_name: str):
    """Init sensor."""

    CoordinatorEntity.__init__(self, coordinator)
  
    self._account_name = account_name
    self._state = None
    self._attributes = {}
    self._last_updated = None

    self.entity_id = generate_entity_id("binary_sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"smol_{self._account_name}_is_on_holiday"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Is On Holiday ({self._account_name})"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:palm-tree"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def is_on(self):
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Determine if current forecast is highlighted by OE."""
    current = now()
    self._state = False
    result: AccountCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    account: SmolAccount | None = result.account if result is not None else None
    if (account is not None):
      _LOGGER.debug(f"Updating SmolIsOnHoliday for '{self._account_name}'")

      self._attributes = {}

      self._state = account.holidayMode is not None and account.holidayMode.config is not None

    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()

    if state is not None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) or state.state is None else state.state.lower() == 'on'
      self._attributes = dict_to_typed_dict(state.attributes)
    
    if (self._state is None):
      self._state = False
    
    _LOGGER.debug(f'Restored SmolIsOnHoliday state: {self._state}')
