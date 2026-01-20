from datetime import datetime
import logging

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
)

from ..utils.requests import calculate_next_refresh

_LOGGER = logging.getLogger(__name__)

class MultiCoordinatorEntity(CoordinatorEntity):
  def __init__(self, primary_coordinator, secondary_coordinators):
    CoordinatorEntity.__init__(self, primary_coordinator)
    self._secondary_coordinators = secondary_coordinators

  async def async_added_to_hass(self) -> None:
    """When entity is added to hass."""
    await super().async_added_to_hass()
    for secondary_coordinator in self._secondary_coordinators:
      self.async_on_remove(
          secondary_coordinator.async_add_listener(
            self._handle_coordinator_update, self.coordinator_context
          )
      )

class BaseCoordinatorResult:
  last_evaluated: datetime
  last_retrieved: datetime
  next_refresh: datetime
  request_attempts: int
  refresh_rate_in_minutes: float
  last_error: Exception | None

  def __init__(self, last_evaluated: datetime, request_attempts: int, refresh_rate_in_minutes: float, last_retrieved: datetime | None = None, last_error: Exception | None = None):
    self.last_evaluated = last_evaluated
    self.last_retrieved = last_retrieved if last_retrieved is not None else last_evaluated
    self.request_attempts = request_attempts
    self.next_refresh = calculate_next_refresh(last_evaluated, request_attempts, refresh_rate_in_minutes)
    self.last_error = last_error
    _LOGGER.debug(f'last_evaluated: {last_evaluated}; last_retrieved: {last_retrieved}; request_attempts: {request_attempts}; refresh_rate_in_minutes: {refresh_rate_in_minutes}; next_refresh: {self.next_refresh}; last_error: {self.last_error}')
