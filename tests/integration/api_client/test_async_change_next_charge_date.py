from datetime import timedelta, datetime
from custom_components.smol.api_client.account import SmolAccount
import pytest

from homeassistant.util.dt import (now)

from integration import get_test_context
from custom_components.smol.api_client import SmolApiClient

def assert_expected_next_charge_date(account_info: SmolAccount, expected_subscription_id: str, expected_next_charge_date: datetime | None):
    assert account_info is not None 
    assert account_info.subscriptions is not None 
    assert len(account_info.subscriptions) > 0

    subscription_discovered = False
    for subscription in account_info.subscriptions:
        if subscription.id == expected_subscription_id:
            subscription_discovered = True
            assert subscription.nextChargeScheduledAt == expected_next_charge_date

    assert subscription_discovered is True

@pytest.mark.asyncio
async def test_when_change_next_charge_date_is_called_then_true_returned():
    # Arrange
    context = get_test_context()

    client = SmolApiClient(context.username, context.password)

    account_info = await client.async_get_account()
    assert account_info is not None 
    assert account_info.subscriptions is not None 
    assert len(account_info.subscriptions) > 0
    expected_address_id = account_info.subscriptions[0].address.id
    expected_subscription_id = account_info.subscriptions[0].id
    original_next_charge_date = account_info.subscriptions[0].nextChargeScheduledAt
    # Always returns 5am regardless what is sent
    expected_next_charge_date = now().replace(hour=5, minute=0, second=0, microsecond=0) + timedelta(days=14)

    try:
        account_info = await client.async_get_account()
        result = await client.async_change_next_charge_date(expected_subscription_id, expected_address_id, expected_next_charge_date)

        # Assert
        assert result is True
        account_info = await client.async_get_account()
        assert_expected_next_charge_date(account_info, expected_subscription_id, expected_next_charge_date)
    finally:
        # Cleanup - return to original state
        if (original_next_charge_date is not None):
            await client.async_change_next_charge_date(expected_subscription_id, expected_address_id, original_next_charge_date)
            account_info = await client.async_get_account()
            assert_expected_next_charge_date(account_info, expected_subscription_id, original_next_charge_date)