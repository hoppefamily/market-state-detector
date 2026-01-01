"""
Example: Using custom configuration.

This example demonstrates how to customize detection thresholds using
a configuration file or programmatically.
"""

from market_state_detector import MarketStateDetector, Config
import tempfile
import os

# Sample closing prices
closing_prices = [
    100, 100.5, 101, 100.8, 101.2, 101.5, 101.3, 101.8, 102, 102.2,
    102.5, 102.3, 102.8, 103, 103.2, 103.5, 103.3, 103.8, 104, 104.2,
    104.5, 104.7, 105, 105.2, 105.5  # Relatively stable data
]

print("=" * 70)
print("EXAMPLE: Custom Configuration")
print("=" * 70)

# Example 1: Default configuration
print("\n1. Using DEFAULT configuration:")
detector_default = MarketStateDetector()
results_default = detector_default.analyze(closing_prices)
print(f"   Stage 1 Detected: {results_default['stage_1_detected']}")

# Example 2: More sensitive configuration (programmatically)
print("\n2. Using SENSITIVE configuration (lower thresholds):")

# Create a temporary config file
config_yaml = """
volatility:
  threshold_multiplier: 1.5  # More sensitive (default: 2.0)
  lookback_period: 20

gaps:
  threshold_percent: 1.0  # More sensitive (default: 2.0)

ranges:
  threshold_percent: 25.0  # More sensitive (default: 50.0)
  lookback_period: 20

general:
  min_data_points: 21
"""

# Write to temp file
with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
    f.write(config_yaml)
    temp_config_path = f.name

try:
    # Load custom config
    config_sensitive = Config(temp_config_path)
    detector_sensitive = MarketStateDetector(config_sensitive)
    results_sensitive = detector_sensitive.analyze(closing_prices)
    
    print(f"   Stage 1 Detected: {results_sensitive['stage_1_detected']}")
    
    if results_sensitive['stage_1_detected']:
        print(f"   Triggered signals: {', '.join(results_sensitive['flags'])}")
finally:
    # Clean up temp file
    os.unlink(temp_config_path)

# Example 3: Less sensitive configuration
print("\n3. Using CONSERVATIVE configuration (higher thresholds):")

config_yaml_conservative = """
volatility:
  threshold_multiplier: 3.0  # Less sensitive (default: 2.0)
  lookback_period: 20

gaps:
  threshold_percent: 5.0  # Less sensitive (default: 2.0)

ranges:
  threshold_percent: 100.0  # Less sensitive (default: 50.0)
  lookback_period: 20

general:
  min_data_points: 21
"""

with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
    f.write(config_yaml_conservative)
    temp_config_path = f.name

try:
    config_conservative = Config(temp_config_path)
    detector_conservative = MarketStateDetector(config_conservative)
    results_conservative = detector_conservative.analyze(closing_prices)
    
    print(f"   Stage 1 Detected: {results_conservative['stage_1_detected']}")
finally:
    os.unlink(temp_config_path)

print("\n" + "=" * 70)
print("\nKey Insight:")
print("Adjust thresholds based on your needs:")
print("  - Lower thresholds = More sensitive, more false positives")
print("  - Higher thresholds = Less sensitive, more false negatives")
print("=" * 70)
