from datetime import date, datetime, time, timedelta
import logging

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id

from homeassistant.util.dt import (utcnow, as_local)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.sensor import (
  RestoreSensor,
  SensorDeviceClass,
)
from homeassistant.exceptions import ServiceValidationError

from ..utils.attributes import dict_to_typed_dict
from ..coordinators.account import AccountCoordinatorResult
from ..api_client.account import SmolSubscription
from ..api_client import SmolApiClient

_LOGGER = logging.getLogger(__name__)

class SmolSubscriptionNextCharge(CoordinatorEntity, RestoreSensor):
  """Sensor for determining the next charge date for the subscription."""

  def __init__(self, hass: HomeAssistant, coordinator, account_name: str, subscription: SmolSubscription, client: SmolApiClient):
    """Init sensor."""

    CoordinatorEntity.__init__(self, coordinator)
  
    self._account_name = account_name
    self._subscription = subscription
    self._client = client
    self._state = None
    self._attributes = {
      "subscription_id": self._subscription.id,
      "product_type_id": self._subscription.product.typeId,
      "product_name": self._subscription.product.name,
    }

    self.entity_id = generate_entity_id("sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"smol_{self._account_name}_{self._subscription.product.typeId}_subscription_next_charge"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Subscription Next Charge {self._subscription.product.name} ({self._account_name})"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:clock"

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
    result: AccountCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    if (result is not None and result.account is not None):
      _LOGGER.debug(f"Updating SmolSubscriptionNextCharge for '{self._account_name}'")

      self._state = None
      for subscription in result.account.subscriptions:
        if subscription.product.typeId == self._subscription.product.typeId:
          self._state = subscription.nextChargeScheduledAt
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
      _LOGGER.debug(f'Restored SmolSubscriptionNextCharge state: {self._state}')

  @callback
  async def async_change_next_charge_date(self, next_charge_date: date):
    """Change next charge date"""
    local_next_charge_date = as_local(datetime.combine(next_charge_date, time(5)))
    if local_next_charge_date < utcnow().replace(hour=5, minute=0, second=0, microsecond=0) + timedelta(days=1):
      raise ServiceValidationError("Next charge time must be in the future")

    result = await self._client.async_change_next_charge_date(self._subscription.id, self._subscription.address.id, local_next_charge_date)
    if result is not True:
      raise ServiceValidationError("Failed to change next charge date")

    await self.coordinator.refresh_account()
