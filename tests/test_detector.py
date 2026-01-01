"""Tests for main detector module."""

import pytest
from market_state_detector import MarketStateDetector, Config


def test_detector_initialization():
    """Test detector initializes correctly."""
    detector = MarketStateDetector()
    
    assert detector.config is not None


def test_analyze_closes_only():
    """Test analysis with only closing prices."""
    # Prices with realistic volatility
    closes = [100, 100.5, 99.8, 100.3, 100.1, 100.6, 100.2, 100.8, 100.5, 101.0,
              100.7, 101.2, 100.9, 101.5, 101.1, 101.7, 101.3, 101.9, 101.6, 102.1,
              101.8, 102.3, 102.0, 102.5, 102.2]
    
    detector = MarketStateDetector()
    results = detector.analyze(closes)
    
    assert 'stage_1_detected' in results
    assert 'signals' in results
    assert 'summary' in results
    assert isinstance(results['stage_1_detected'], bool)


def test_analyze_with_spike():
    """Test that volatility spike is detected."""
    # Prices with realistic volatility then large jump
    closes = [100, 100.5, 99.8, 100.3, 100.1, 100.6, 100.2, 100.8, 100.5, 101.0,
              100.7, 101.2, 100.9, 101.5, 101.1, 101.7, 101.3, 101.9, 101.6, 102.1,
              101.8, 102.3, 102.0, 102.5, 110.0]  # Large spike
    
    detector = MarketStateDetector()
    results = detector.analyze(closes)
    
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


def test_analyze_simple():
    """Test simple analysis method."""
    # Prices with realistic volatility
    closes = [100, 100.5, 99.8, 100.3, 100.1, 100.6, 100.2, 100.8, 100.5, 101.0,
              100.7, 101.2, 100.9, 101.5, 101.1, 101.7, 101.3, 101.9, 101.6, 102.1,
              101.8, 102.3, 102.0, 102.5, 102.2]
    
    detector = MarketStateDetector()
    result = detector.analyze_simple(closes)
    
    assert isinstance(result, bool)


def test_detector_with_custom_config():
    """Test detector with custom configuration."""
    config = Config()
    detector = MarketStateDetector(config)
    
    # Prices with realistic volatility
    closes = [100, 100.5, 99.8, 100.3, 100.1, 100.6, 100.2, 100.8, 100.5, 101.0,
              100.7, 101.2, 100.9, 101.5, 101.1, 101.7, 101.3, 101.9, 101.6, 102.1,
              101.8, 102.3, 102.0, 102.5, 102.2]
    results = detector.analyze(closes)
    
    assert 'stage_1_detected' in results
