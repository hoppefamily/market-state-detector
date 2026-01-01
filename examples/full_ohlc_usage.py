"""
Example: Using the detector with full OHLC data.

This example shows how to analyze data with Open, High, Low, Close prices
to enable all detection methods (volatility, gaps, and ranges).
"""

from market_state_detector import MarketStateDetector, Config

# Sample OHLC data for 25 days
# Format: [open, high, low, close]
ohlc_data = [
    [100, 102, 99, 101],
    [101, 103, 100, 102],
    [102, 104, 101, 103],
    [103, 105, 102, 104],
    [104, 106, 103, 105],
    [105, 107, 104, 106],
    [106, 108, 105, 107],
    [107, 109, 106, 108],
    [108, 110, 107, 109],
    [109, 111, 108, 110],
    [110, 112, 109, 111],
    [111, 113, 110, 112],
    [112, 114, 111, 113],
    [113, 115, 112, 114],
    [114, 116, 113, 115],
    [115, 117, 114, 116],
    [116, 118, 115, 117],
    [117, 119, 116, 118],
    [118, 120, 117, 119],
    [119, 121, 118, 120],
    [120, 122, 119, 121],
    [121, 123, 120, 122],
    [122, 124, 121, 123],
    [123, 125, 122, 124],
    [130, 135, 124, 127],  # Large gap up and wide range
]

# Separate into individual lists
opens = [day[0] for day in ohlc_data]
highs = [day[1] for day in ohlc_data]
lows = [day[2] for day in ohlc_data]
closes = [day[3] for day in ohlc_data]

# Create detector with default config
detector = MarketStateDetector()

# Analyze with full OHLC data
results = detector.analyze(
    closes=closes,
    highs=highs,
    lows=lows,
    opens=opens
)

# Display results
print("=" * 70)
print("EXAMPLE: Full OHLC Market State Detection")
print("=" * 70)
print(f"\nStage 1 Detected: {results['stage_1_detected']}")
print(f"Triggered Signals: {', '.join(results['flags']) if results['flags'] else 'None'}")
print(f"\n{results['summary']}")

if results['stage_1_detected']:
    print("\nDetailed Analysis:")
    
    for signal_name, signal_data in results['signals'].items():
        print(f"\n  {signal_name.upper().replace('_', ' ')}:")
        print(f"    Detected: {signal_data['detected']}")
        
        if 'details' in signal_data:
            for key, value in signal_data['details'].items():
                if isinstance(value, float):
                    print(f"    {key}: {value:.4f}")
                else:
                    print(f"    {key}: {value}")

print("\n" + "=" * 70)
