"""Shared pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_stable_prices():
    """Fixture providing stable price data."""
    return [100 + i * 0.5 for i in range(25)]


@pytest.fixture
def sample_volatile_prices():
    """Fixture providing volatile price data."""
    prices = [100 + i * 0.5 for i in range(24)]
    prices.append(120)  # Large spike
    return prices


@pytest.fixture
def sample_ohlc_data():
    """Fixture providing full OHLC data."""
    closes = [100 + i for i in range(25)]
    highs = [c + 2 for c in closes]
    lows = [c - 2 for c in closes]
    opens = closes.copy()
    
    return {
        'closes': closes,
        'highs': highs,
        'lows': lows,
        'opens': opens
    }
