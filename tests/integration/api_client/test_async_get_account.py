import pytest

from homeassistant.util.dt import (now)

from integration import get_test_context
from custom_components.smol.api_client import SmolApiClient

@pytest.mark.asyncio
async def test_when_get_account_is_called_then_details_returned():
    # Arrange
    context = get_test_context()

    client = SmolApiClient(context.username, context.password)

    # Act
    result = await client.async_get_account()

    # Assert
    assert result is not None
    assert result.holidayMode is not None

    if (result.holidayMode.config is not None):
        assert result.holidayMode.config.endDate >= now()

    assert result.subscriptions is not None
    assert len(result.subscriptions) > 0
    
    for subscription in result.subscriptions:
        assert subscription.product is not None
        assert subscription.product.typeId is not None
        assert subscription.product.name is not None
        assert subscription.product.packSize > 0