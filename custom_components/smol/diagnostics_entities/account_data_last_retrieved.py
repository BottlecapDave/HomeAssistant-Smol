from .base import SmolBaseDataLastRetrieved

class SmolAccountDataLastRetrieved(SmolBaseDataLastRetrieved):
  """Sensor for displaying the last time the account data was last retrieved."""

  def __init__(self, hass, coordinator, account_name):
    """Init sensor."""
    self._account_name = account_name
    SmolBaseDataLastRetrieved.__init__(self, hass, coordinator)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"smol_{self._account_name}_account_data_last_retrieved"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Account Data Last Retrieved ({self._account_name})"