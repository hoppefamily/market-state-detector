#!/usr/bin/env python
"""
Quick stock check using IBKR data.

Usage:
    python check_stock.py AAPL
    python check_stock.py TSLA
    python check_stock.py        # defaults to SPY

Requirements:
    - ib_insync installed (pip install ib_insync)
    - TWS or IB Gateway running on port 4001
    - API connections enabled
"""

import sys

from market_state_detector import MarketStateDetector

try:
    from market_state_detector.ibkr_data import fetch_ibkr_data
except ImportError:
    print("ERROR: ib_insync library is not installed.")
    print("Install with: pip install ib_insync")
    sys.exit(1)

# Get symbol from command line, default to SPY
symbol = sys.argv[1].upper() if len(sys.argv) > 1 else 'SPY'

try:
    print(f"\nFetching {symbol} data from IBKR...")

    # Fetch data
    data = fetch_ibkr_data(symbol, days=30, port=4001)

    # Analyze
    detector = MarketStateDetector()
    results = detector.analyze(**data)

    # Print result
    print(f"\n{'='*60}")
    print(f"{symbol} - MARKET STATE CHECK")
    print(f"{'='*60}")
    print(f"\n{results['summary']}\n")
    print(f"{'='*60}\n")

    # Exit code: 0 if normal, 1 if Stage 1 detected
    sys.exit(1 if results['stage_1_detected'] else 0)

except Exception as e:
    print(f"\nERROR: {e}")
    print("\nMake sure:")
    print("  - IB Gateway/TWS is running")
    print("  - API connections are enabled")
    print("  - Symbol is valid")
    sys.exit(2)
