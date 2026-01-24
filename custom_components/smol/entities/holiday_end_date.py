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
from homeassistant.components.sensor import (
  RestoreSensor,
  SensorDeviceClass,
)

from ..utils.attributes import dict_to_typed_dict
from ..coordinators.account import AccountCoordinatorResult

_LOGGER = logging.getLogger(__name__)

class SmolHolidayEndDate(CoordinatorEntity, RestoreSensor):
  """Sensor for determining the configured end holiday date."""

  def __init__(self, hass: HomeAssistant, coordinator, account_name: str):
    """Init sensor."""

    CoordinatorEntity.__init__(self, coordinator)
  
    self._account_name = account_name
    self._state = None
    self._attributes = {}

    self.entity_id = generate_entity_id("sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"smol_{self._account_name}_holiday_end_date"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Holiday End Date ({self._account_name})"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:palm-tree"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes
  
  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.TIMESTAMP
  
  @property
  def native_value(self):
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    # Find the current rate. We only need to do this every half an hour
    current = now()
    result: AccountCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    if (result is not None and result.account is not None):
      _LOGGER.debug(f"Updating SmolHolidayEndDate for '{self._account_name}'")

      self._state = result.account.holidayMode.config.endDate if result.account.holidayMode is not None and result.account.holidayMode.config is not None else None
    else:
      self._state = None

    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    last_sensor_state = await self.async_get_last_sensor_data()
    
    if state is not None and last_sensor_state is not None and self._state is None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else last_sensor_state.native_value
      self._attributes = dict_to_typed_dict(state.attributes, [])
      _LOGGER.debug(f'Restored SmolHolidayEndDate state: {self._state}')
