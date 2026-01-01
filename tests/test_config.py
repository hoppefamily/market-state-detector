"""Tests for configuration module."""

import pytest
import tempfile
import os
from market_state_detector.config import Config


def test_default_config():
    """Test default configuration loads correctly."""
    config = Config()
    
    assert config.get("volatility", "threshold_multiplier") == 2.0
    assert config.get("gaps", "threshold_percent") == 2.0
    assert config.get("ranges", "threshold_percent") == 50.0


def test_load_from_file():
    """Test loading configuration from file."""
    config_yaml = """
volatility:
  threshold_multiplier: 3.0
  lookback_period: 30

gaps:
  threshold_percent: 5.0
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_yaml)
        temp_path = f.name
    
    try:
        config = Config(temp_path)
        
        assert config.get("volatility", "threshold_multiplier") == 3.0
        assert config.get("volatility", "lookback_period") == 30
        assert config.get("gaps", "threshold_percent") == 5.0
        # Default value should still be present
        assert config.get("ranges", "threshold_percent") == 50.0
    finally:
        os.unlink(temp_path)


def test_get_section():
    """Test getting entire configuration section."""
    config = Config()
    
    vol_section = config.get_section("volatility")
    
    assert isinstance(vol_section, dict)
    assert "threshold_multiplier" in vol_section
    assert "lookback_period" in vol_section


def test_nonexistent_file():
    """Test that nonexistent file doesn't crash."""
    # Should just use defaults when file doesn't exist
    config = Config("/nonexistent/path/config.yaml")
    
    assert config.get("volatility", "threshold_multiplier") == 2.0
