import pytest
import mock

from homeassistant.util.dt import (as_utc, parse_datetime)

from custom_components.smol.api_client import SmolApiClient, RequestException, ServerException, AuthenticationException
from custom_components.smol.config.main import async_validate_main_config
from custom_components.smol.const import (
  CONFIG_ACCOUNT_NAME,
  CONFIG_ACCOUNT_USERNAME,
  CONFIG_ACCOUNT_PASSWORD
)
from . import assert_errors_not_present

now = as_utc(parse_datetime("2023-08-20T10:00:00Z"))
mpan = "selected-mpan"

def get_account_info(tariff_code: str = "E-1R-SUPER-GREEN-24M-21-07-30-C"):
  return {
    "electricity_meter_points": [
      {
        "mpan": mpan,
        "agreements": [
          {
            "start": "2023-08-01T00:00:00+01:00",
            "end": "2023-09-01T00:00:00+01:00",
            "tariff_code": tariff_code,
            "product_code": "SUPER-GREEN-24M-21-07-30"
          }
        ]
      }
    ]
  }

config_keys = [
  CONFIG_ACCOUNT_NAME, 
  CONFIG_ACCOUNT_USERNAME,
  CONFIG_ACCOUNT_PASSWORD
]

@pytest.mark.asyncio
async def test_when_data_is_valid_then_no_errors_returned():
  # Arrange
  data = {
    CONFIG_ACCOUNT_NAME: "main",
    CONFIG_ACCOUNT_USERNAME: "user@user.com",
    CONFIG_ACCOUNT_PASSWORD: "password123"
  }

  account_info = get_account_info()
  async def async_mocked_get_account(*args, **kwargs):
    return account_info

  # Act
  with mock.patch.multiple(SmolApiClient, async_get_account=async_mocked_get_account):
    errors = await async_validate_main_config(data)

    # Assert
    assert_errors_not_present(errors, config_keys)

@pytest.mark.asyncio
async def test_when_account_info_not_found_then_errors_returned():
  # Arrange
  data = {
    CONFIG_ACCOUNT_NAME: "main",
    CONFIG_ACCOUNT_USERNAME: "user@user.com",
    CONFIG_ACCOUNT_PASSWORD: "password123"
  }

  async def async_mocked_get_account(*args, **kwargs):
    return None

  # Act
  with mock.patch.multiple(SmolApiClient, async_get_account=async_mocked_get_account):
    errors = await async_validate_main_config(data)

    # Assert
    assert CONFIG_ACCOUNT_USERNAME in errors
    assert errors[CONFIG_ACCOUNT_USERNAME] == "account_not_found"
    
    assert_errors_not_present(errors, config_keys, CONFIG_ACCOUNT_USERNAME)

@pytest.mark.asyncio
async def test_when_account_info_raises_server_error_then_errors_returned():
  # Arrange
  data = {
    CONFIG_ACCOUNT_NAME: "main",
    CONFIG_ACCOUNT_USERNAME: "user@user.com",
    CONFIG_ACCOUNT_PASSWORD: "password123"
  }

  async def async_mocked_get_account(*args, **kwargs):
    raise ServerException()

  # Act
  with mock.patch.multiple(SmolApiClient, async_get_account=async_mocked_get_account):
    errors = await async_validate_main_config(data)

    # Assert
    assert CONFIG_ACCOUNT_USERNAME in errors
    assert errors[CONFIG_ACCOUNT_USERNAME] == "server_error"
    
    assert_errors_not_present(errors, config_keys, CONFIG_ACCOUNT_USERNAME)

@pytest.mark.asyncio
async def test_when_account_info_raises_request_error_then_errors_returned():
  # Arrange
  data = {
    CONFIG_ACCOUNT_NAME: "main",
    CONFIG_ACCOUNT_USERNAME: "user@user.com",
    CONFIG_ACCOUNT_PASSWORD: "password123"
  }

  async def async_mocked_get_account(*args, **kwargs):
    raise RequestException("blah", [])

  # Act
  with mock.patch.multiple(SmolApiClient, async_get_account=async_mocked_get_account):
    errors = await async_validate_main_config(data)

    # Assert
    assert CONFIG_ACCOUNT_USERNAME in errors
    assert errors[CONFIG_ACCOUNT_USERNAME] == "account_not_found"
    
    assert_errors_not_present(errors, config_keys, CONFIG_ACCOUNT_USERNAME)