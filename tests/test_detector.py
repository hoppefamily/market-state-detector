"""Tests for main detector module."""

import pytest
from market_state_detector import MarketStateDetector, Config


def test_detector_initialization():
    """Test detector initializes correctly."""
    detector = MarketStateDetector()
    
    assert detector.config is not None


def test_analyze_closes_only(sample_stable_prices):
    """Test analysis with only closing prices."""
    detector = MarketStateDetector()
    results = detector.analyze(sample_stable_prices)
    
    assert 'stage_1_detected' in results
    assert 'signals' in results
    assert 'summary' in results
    assert isinstance(results['stage_1_detected'], bool)


def test_analyze_with_spike(sample_volatile_prices):
    """Test that volatility spike is detected."""
    detector = MarketStateDetector()
    results = detector.analyze(sample_volatile_prices)
    
    assert results['stage_1_detected'] is True
    assert 'volatility_spike' in results['signals']
    assert results['signals']['volatility_spike']['detected'] is True


def test_analyze_full_ohlc():
    """Test analysis with full OHLC data."""
    # Normal data
    closes = [100 + i for i in range(25)]
    highs = [c + 2 for c in closes]
    lows = [c - 2 for c in closes]
    opens = closes.copy()
    
    detector = MarketStateDetector()
    results = detector.analyze(closes, highs=highs, lows=lows, opens=opens)
    
    assert 'stage_1_detected' in results
    assert 'volatility_spike' in results['signals']
    assert 'price_gap' in results['signals']
    assert 'wide_range' in results['signals']


def test_analyze_insufficient_data():
    """Test that insufficient data raises ValueError."""
    closes = [100, 101, 102]  # Only 3 points
    
    detector = MarketStateDetector()
    
    with pytest.raises(ValueError):
        detector.analyze(closes)


def test_analyze_simple(sample_stable_prices):
    """Test simple analysis method."""
    detector = MarketStateDetector()
    result = detector.analyze_simple(sample_stable_prices)
    
    assert isinstance(result, bool)


def test_detector_with_custom_config(sample_stable_prices):
    """Test detector with custom configuration."""
    config = Config()
    detector = MarketStateDetector(config)
    
    results = detector.analyze(sample_stable_prices)
    
    assert 'stage_1_detected' in results
