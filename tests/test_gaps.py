"""Tests for gap detection module."""

import pytest
from market_state_detector.gaps import detect_gap, detect_gap_from_prices


def test_detect_gap_no_gap():
    """Test detection with no significant gap."""
    gap_detected, details = detect_gap(100, 101, threshold_percent=2.0)
    
    assert gap_detected is False
    assert details['gap_percent'] == 1.0
    assert details['gap_direction'] == 'up'


def test_detect_gap_up():
    """Test detection of gap up."""
    gap_detected, details = detect_gap(100, 105, threshold_percent=2.0)
    
    assert gap_detected is True
    assert details['gap_percent'] == 5.0
    assert details['gap_direction'] == 'up'


def test_detect_gap_down():
    """Test detection of gap down."""
    gap_detected, details = detect_gap(100, 97, threshold_percent=2.0)
    
    assert gap_detected is True
    assert details['gap_percent'] == -3.0
    assert details['gap_direction'] == 'down'


def test_detect_gap_invalid_prices():
    """Test that invalid prices raise ValueError."""
    with pytest.raises(ValueError):
        detect_gap(0, 100)
    
    with pytest.raises(ValueError):
        detect_gap(100, -50)


def test_detect_gap_from_prices():
    """Test gap detection from price lists."""
    closes = [100, 101, 102, 103, 104]
    opens = [100.5, 101.5, 102.5, 103.5, 109]  # Last open has large gap
    
    gap_detected, details = detect_gap_from_prices(closes, opens, threshold_percent=2.0)
    
    assert gap_detected is True
    assert details['gap_direction'] == 'up'


def test_detect_gap_from_prices_insufficient():
    """Test that insufficient data raises ValueError."""
    closes = [100]
    opens = [100.5]
    
    with pytest.raises(ValueError):
        detect_gap_from_prices(closes, opens)
