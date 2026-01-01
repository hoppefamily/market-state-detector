"""Tests for range detection module."""

import pytest
from market_state_detector.ranges import (
    calculate_range_percent,
    calculate_average_range,
    detect_wide_range
)


def test_calculate_range_percent():
    """Test range percentage calculation."""
    range_pct = calculate_range_percent(high=105, low=95, close=100)
    
    assert range_pct == 10.0  # (105-95)/100 * 100 = 10%


def test_calculate_range_percent_invalid():
    """Test that invalid prices raise ValueError."""
    with pytest.raises(ValueError):
        calculate_range_percent(high=0, low=95, close=100)
    
    with pytest.raises(ValueError):
        calculate_range_percent(high=95, low=100, close=100)  # High < Low


def test_calculate_average_range():
    """Test average range calculation."""
    highs = [102, 103, 104, 105, 106]
    lows = [98, 99, 100, 101, 102]
    closes = [100, 101, 102, 103, 104]
    
    avg = calculate_average_range(highs, lows, closes, period=5)
    
    assert avg > 0
    assert isinstance(avg, float)


def test_calculate_average_range_mismatched():
    """Test that mismatched lists raise ValueError."""
    highs = [102, 103]
    lows = [98, 99, 100]
    closes = [100, 101]
    
    with pytest.raises(ValueError):
        calculate_average_range(highs, lows, closes, period=2)


def test_detect_wide_range_normal():
    """Test detection with normal range."""
    # Create data with consistent ranges
    highs = [100 + i + 2 for i in range(25)]
    lows = [100 + i - 2 for i in range(25)]
    closes = [100 + i for i in range(25)]
    
    wide_detected, details = detect_wide_range(
        highs, lows, closes, threshold_percent=50.0
    )
    
    assert wide_detected is False


def test_detect_wide_range_detected():
    """Test detection with wide range."""
    # Create data with normal ranges then wide range
    highs = [100 + i + 2 for i in range(24)]
    lows = [100 + i - 2 for i in range(24)]
    closes = [100 + i for i in range(24)]
    
    # Add day with very wide range
    highs.append(135)
    lows.append(115)
    closes.append(125)
    
    wide_detected, details = detect_wide_range(
        highs, lows, closes, threshold_percent=50.0
    )
    
    assert wide_detected is True
    assert details['range_expansion'] > 0


def test_detect_wide_range_insufficient_data():
    """Test that insufficient data raises ValueError."""
    highs = [102, 103]
    lows = [98, 99]
    closes = [100, 101]
    
    with pytest.raises(ValueError):
        detect_wide_range(highs, lows, closes, lookback_period=20)
