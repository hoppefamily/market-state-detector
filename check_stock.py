#!/usr/bin/env python
"""
Quick stock check using Alpaca (default) or IBKR data.

Usage:
    python check_stock.py AAPL
    python check_stock.py TSLA --broker ibkr
    python check_stock.py        # defaults to SPY, Alpaca
    python check_stock.py MSFT --broker alpaca

Arguments:
    symbol         Stock ticker (default: SPY)
    --broker       Data source: 'alpaca' (default) or 'ibkr'

Requirements:
    - For Alpaca: alpaca-py installed, API keys set (see docs/quick-reference/ALPACA_QUICK_REFERENCE.md)
    - For IBKR: ib_insync installed, TWS or IB Gateway running on port 4001, API enabled
"""


import argparse
import logging
import sys

from market_state_detector import MarketStateDetector


def main():
    parser = argparse.ArgumentParser(description="Quick stock check using Alpaca (default) or IBKR data.")
    parser.add_argument('symbol', nargs='?', default='SPY', help='Stock ticker (default: SPY)')
    parser.add_argument('--broker', choices=['alpaca', 'ibkr'], default='alpaca', help="Data source: 'alpaca' (default) or 'ibkr'")
    args = parser.parse_args()

    symbol = args.symbol.upper()
    broker = args.broker.lower()

    if broker == 'ibkr':
        try:
            from market_state_detector.ibkr_data import IBKRDataFetcher
        except ImportError:
            print("ERROR: ib_insync library is not installed.")
            print("Install with: pip install ib_insync")
            sys.exit(1)
        # Suppress ib_insync informational messages
        logging.getLogger('ib_insync').setLevel(logging.ERROR)
        print(f"\nFetching {symbol} data from IBKR...")
        try:
            fetcher = IBKRDataFetcher(port=4001)
            fetcher.connect()
            data = fetcher.fetch_daily_bars(symbol, days=30)
        except Exception as e:
            print(f"\nERROR: {e}")
            print("\nMake sure:")
            print("  - IB Gateway/TWS is running")
            print("  - API connections are enabled")
            print("  - Symbol is valid")
            sys.exit(2)
    else:
        try:
            from market_state_detector.alpaca_data import AlpacaDataFetcher
        except ImportError:
            print("ERROR: alpaca-py library is not installed.")
            print("Install with: pip install alpaca-py")
            sys.exit(1)
        print(f"\nFetching {symbol} data from Alpaca...")
        try:
            fetcher = AlpacaDataFetcher(paper=True)
            data = fetcher.fetch_daily_bars(symbol, days=30)
        except Exception as e:
            print(f"\nERROR: {e}")
            print("\nMake sure:")
            print("  - ALPACA_API_KEY and ALPACA_SECRET_KEY are set (env or .env)")
            print("  - Symbol is valid (US stocks/ETFs only)")
            sys.exit(2)

    # Analyze with market context
    detector = MarketStateDetector(symbol=symbol)
    results = detector.analyze_with_context(
        symbol=symbol,
        fetcher=fetcher,
        include_context=True,
        **data
    )

    # Print result
    print(f"\n{'='*60}")
    print(f"{symbol} - MARKET STATE CHECK")
    print(f"{'='*60}")
    print(f"\n{results['summary']}")

    # Print market context if available
    if results.get('market_context') and results['market_context']['message']:
        print(results['market_context']['message'])

    print(f"\n{'='*60}\n")

    # Exit code: 0 if normal, 1 if Stage 1 detected
    sys.exit(1 if results['stage_1_detected'] else 0)


if __name__ == "__main__":
    main()
