from datetime import timedelta
import pytest

from homeassistant.util.dt import (now)

from integration import get_test_context
from custom_components.smol.api_client import SmolApiClient

@pytest.mark.asyncio
async def test_when_start_holiday_mode_is_called_then_true_returned():
    # Arrange
    context = get_test_context()

    client = SmolApiClient(context.username, context.password)
    expected_end_date = now().replace(minute=0, second=0, microsecond=0) + timedelta(days=1)

    # If in holiday mode, temp switch off
    original_end_date = None
    account_info = await client.async_get_account()
    if (account_info is not None and 
        account_info.holidayMode is not None and 
        account_info.holidayMode.config is not None):
        original_end_date = account_info.holidayMode.config.endDate

        await client.async_end_holiday()

    # Act
    try:
        result = await client.async_start_holiday(expected_end_date)
        account_info = await client.async_get_account()

        # Assert
        assert result is True
        assert account_info is not None
        assert account_info.holidayMode is not None
        assert account_info.holidayMode.config is not None
        assert account_info.holidayMode.config.endDate == expected_end_date
    finally:
        # Cleanup - return to original state
        if (original_end_date is not None):
            await client.async_end_holiday()
            await client.async_start_holiday(original_end_date)