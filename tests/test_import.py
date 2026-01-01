"""Basic test to ensure package imports work."""

def test_import():
    """Test that the package can be imported."""
    import market_state_detector
    
    assert hasattr(market_state_detector, 'MarketStateDetector')
    assert hasattr(market_state_detector, 'Config')
    assert hasattr(market_state_detector, '__version__')


def test_version():
    """Test that version is defined."""
    import market_state_detector
    
    assert market_state_detector.__version__ == "0.1.0"
