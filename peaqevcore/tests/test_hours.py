import pytest
import statistics as stat
from ..services.hourselection.initializers.regular_hours import RegularHours
from ..services.hourselection.initializers.price_aware_hours import PriceAwareHours



class MockOptions:
    def __init__(self, nonhours, cautionhours):
        self.nonhours = nonhours
        self.cautionhours = cautionhours

class MockHub:
    def __init__(self, options):
        self.options = options


def test_regular_hours_non_initialized():
    options = MockOptions([0,1,2], [23])
    hub = MockHub(options)
    h = RegularHours(hub)
    
    assert h.is_initialized == True
    assert hasattr(h, 'timer') == True
    assert hasattr(h, 'scheduler') == True


@pytest.mark.asyncio
async def test_price_aware_update_prices():
    options = MockOptions([0,1,2], [23])
    hub = MockHub(options)
    h = PriceAwareHours(hub)
    await h.async_update_prices()
    assert h.is_initialized == True
    assert hasattr(h, 'timer') == True
    assert hasattr(h, 'scheduler') == True
    assert hasattr(h, 'prices') == True
    assert hasattr(h, 'prices_tomorrow') == True
    assert hasattr(h, 'future_hours') == True
    assert hasattr(h, 'non_hours') == True
    assert hasattr(h, 'caution_hours') == True
    assert hasattr(h, 'dynamic_caution_hours') == True
    assert hasattr(h, 'cautionhour_type_string') == True
    assert hasattr(h, 'absolute_top_price') == True
    assert hasattr(h, 'min_price') == True
    assert hasattr(h, 'options') == True
    assert hasattr(h, 'scheduler') == True