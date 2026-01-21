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
from ..api_client.account import SmolSubscription

_LOGGER = logging.getLogger(__name__)

class SmolSubscriptionQuantity(CoordinatorEntity, RestoreSensor):
  """Sensor for determining the quantity of the subscription."""

  def __init__(self, hass: HomeAssistant, coordinator, account_name: str, subscription: SmolSubscription):
    """Init sensor."""

    CoordinatorEntity.__init__(self, coordinator)
  
    self._account_name = account_name
    self._subscription = subscription
    self._state = None
    self._attributes = {
      "product_type_id": self._subscription.product.typeId,
      "product_name": self._subscription.product.name,
    }

    self.entity_id = generate_entity_id("sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"smol_{self._account_name}_{self._subscription.product.typeId}_subscription_quantity"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Subscription Quantity {self._subscription.product.typeId} ({self._account_name})"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:numeric"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes
  
  @property
  def native_value(self):
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Retrieve the current rate for the sensor."""
    # Find the current rate. We only need to do this every half an hour
    current = now()
    result: AccountCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    if (result is not None and result.account is not None):
      _LOGGER.debug(f"Updating SmolSubscriptionQuantity for '{self._account_name}'")

      self._state = None
      for subscription in result.account.subscriptions:
        if subscription.product.typeId == self._subscription.product.typeId:
          self._state = subscription.product.packSize
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
      _LOGGER.debug(f'Restored SmolSubscriptionQuantity state: {self._state}')
