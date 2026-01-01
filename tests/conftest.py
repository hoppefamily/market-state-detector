"""Shared pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_stable_prices():
    """Fixture providing stable price data."""
    return [100, 100.5, 99.8, 100.3, 100.1, 100.6, 100.2, 100.8, 100.5, 101.0,
            100.7, 101.2, 100.9, 101.5, 101.1, 101.7, 101.3, 101.9, 101.6, 102.1,
            101.8, 102.3, 102.0, 102.5, 102.2]


@pytest.fixture
def sample_volatile_prices():
    """Fixture providing volatile price data."""
    return [100, 100.5, 99.8, 100.3, 100.1, 100.6, 100.2, 100.8, 100.5, 101.0,
            100.7, 101.2, 100.9, 101.5, 101.1, 101.7, 101.3, 101.9, 101.6, 102.1,
            101.8, 102.3, 102.0, 102.5, 110.0]  # Large spike


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
