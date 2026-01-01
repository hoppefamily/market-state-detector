"""Tests for volatility detection module."""

import pytest
from market_state_detector.volatility import (
    calculate_daily_returns,
    calculate_volatility,
    detect_volatility_spike
)


def test_calculate_daily_returns():
    """Test daily returns calculation."""
    prices = [100, 102, 101, 103]
    returns = calculate_daily_returns(prices)
    
    assert len(returns) == 3
    assert abs(returns[0] - 0.02) < 0.0001  # (102-100)/100 = 0.02
    assert abs(returns[1] - (-0.0098)) < 0.0001  # (101-102)/102 ≈ -0.0098


def test_calculate_daily_returns_empty():
    """Test that empty prices raise ValueError."""
    with pytest.raises(ValueError):
        calculate_daily_returns([])


def test_calculate_daily_returns_insufficient():
    """Test that single price raises ValueError."""
    with pytest.raises(ValueError):
        calculate_daily_returns([100])


def test_calculate_volatility():
    """Test volatility calculation."""
    returns = [0.01, -0.01, 0.02, -0.02, 0.01]
    vol = calculate_volatility(returns)
    
    assert vol > 0
    assert isinstance(vol, float)


def test_calculate_volatility_empty():
    """Test that empty returns raise ValueError."""
    with pytest.raises(ValueError):
        calculate_volatility([])


def test_detect_volatility_spike_normal():
    """Test detection with normal volatility."""
    # Prices with realistic volatility (small random-like movements)
    prices = [100, 100.5, 99.8, 100.3, 100.1, 100.6, 100.2, 100.8, 100.5, 101.0,
              100.7, 101.2, 100.9, 101.5, 101.1, 101.7, 101.3, 101.9, 101.6, 102.1,
              101.8, 102.3, 102.0, 102.5, 102.2]
    
    spike_detected, details = detect_volatility_spike(prices)
    
    assert spike_detected is False
    assert 'recent_return' in details
    assert 'historical_volatility' in details


def test_detect_volatility_spike_detected():
    """Test detection with volatility spike."""
    # Prices with realistic volatility then large jump
    prices = [100, 100.5, 99.8, 100.3, 100.1, 100.6, 100.2, 100.8, 100.5, 101.0,
              100.7, 101.2, 100.9, 101.5, 101.1, 101.7, 101.3, 101.9, 101.6, 102.1,
              101.8, 102.3, 102.0, 102.5, 110.0]  # Large spike
    
    spike_detected, details = detect_volatility_spike(prices)
    
    assert spike_detected is True
    assert details['spike_magnitude'] > 1.0


def test_detect_volatility_spike_insufficient_data():
    """Test that insufficient data raises ValueError."""
    prices = [100, 101, 102]
    
    with pytest.raises(ValueError):
        detect_volatility_spike(prices, lookback_period=20)
