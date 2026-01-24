from datetime import timedelta
import pytest

from homeassistant.util.dt import (now)

from integration import get_test_context
from custom_components.smol.api_client import SmolApiClient

@pytest.mark.asyncio
async def test_when_end_holiday_mode_is_called_then_details_returned():
    # Arrange
    context = get_test_context()

    client = SmolApiClient(context.username, context.password)
    expected_end_date = None

    # If not holiday mode, set so we can turn off
    original_end_date = None
    account_info = await client.async_get_account()
    if (account_info is not None and 
        account_info.holidayMode is not None and 
        account_info.holidayMode.config is not None):
        original_end_date = account_info.holidayMode.config.endDate
        expected_end_date = original_end_date
    else:
        expected_end_date = now().replace(minute=0, second=0, microsecond=0) + timedelta(days=1)
        await client.async_start_holiday(expected_end_date)

    try:
        # Make sure holiday is set
        account_info = await client.async_get_account()
        assert account_info is not None
        assert account_info.holidayMode is not None
        assert account_info.holidayMode.config is not None
        assert account_info.holidayMode.config.endDate == expected_end_date

        result = await client.async_end_holiday()
        account_info = await client.async_get_account()

        # Assert
        assert result is True
        assert account_info is not None
        assert account_info.holidayMode is not None
        assert account_info.holidayMode.config is None
    finally:
        # Cleanup - return to original state
        if (original_end_date is not None):
            await client.async_start_holiday(original_end_date)