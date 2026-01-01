"""
Example: Basic usage of the market state detector.

This example demonstrates how to use the detector with simple closing price data.
"""

from market_state_detector import MarketStateDetector

# Sample closing prices (most recent last)
# This simulates 30 days of data with a recent volatility spike
closing_prices = [
    100.0, 101.0, 100.5, 102.0, 101.5, 103.0, 102.5, 104.0, 103.5, 105.0,
    104.5, 106.0, 105.5, 107.0, 106.5, 108.0, 107.5, 109.0, 108.5, 110.0,
    109.5, 111.0, 110.5, 112.0, 111.5, 113.0, 112.5, 114.0, 113.5, 120.0  # Large spike
]

# Create detector with default configuration
detector = MarketStateDetector()

# Perform analysis
results = detector.analyze(closing_prices)

# Display results
print("=" * 70)
print("EXAMPLE: Basic Market State Detection")
print("=" * 70)
print(f"\nStage 1 Detected: {results['stage_1_detected']}")
print(f"\n{results['summary']}")

if results['stage_1_detected']:
    print("\nDetailed Signal Information:")
    for signal_name, signal_data in results['signals'].items():
        if signal_data['detected']:
            print(f"\n  {signal_name.upper().replace('_', ' ')}:")
            for key, value in signal_data['details'].items():
                if isinstance(value, float):
                    print(f"    {key}: {value:.4f}")
                else:
                    print(f"    {key}: {value}")

print("\n" + "=" * 70)
