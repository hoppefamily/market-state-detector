"""
Example: Using Alpaca Markets data with the market state detector.

This example demonstrates how to fetch daily OHLC data from Alpaca Markets
and analyze it with the MarketStateDetector.

Prerequisites:
    1. Install alpaca-py: pip install alpaca-py
    2. Sign up for free Alpaca account at https://alpaca.markets/
    3. Get your API keys from the Alpaca dashboard
    4. Set environment variables or pass keys directly:
       export ALPACA_API_KEY="your_api_key"
       export ALPACA_SECRET_KEY="your_secret_key"

Note: Alpaca only supports US equities. No forex, futures, or international stocks.
"""

import os

from market_state_detector import MarketStateDetector

try:
    from market_state_detector.alpaca_data import AlpacaDataFetcher, fetch_alpaca_data
except ImportError:
    print("ERROR: alpaca-py library is not installed.")
    print("Install with: pip install alpaca-py")
    exit(1)


def example_simple_fetch():
    """
    Simple example: Fetch data and analyze with convenience function.
    """
    print("=" * 70)
    print("EXAMPLE 1: Simple Alpaca Data Fetch")
    print("=" * 70)

    try:
        # Fetch data using convenience function
        # This uses paper trading by default (safe for testing)
        print("\nFetching 30 days of AAPL data from Alpaca...")
        data = fetch_alpaca_data(
            symbol='AAPL',
            days=30,
            paper=True  # Paper trading (default)
        )

        print(f"Retrieved {len(data['closes'])} daily bars")
        print(f"Price range: ${data['closes'][0]:.2f} -> ${data['closes'][-1]:.2f}")

        # Analyze with detector
        detector = MarketStateDetector()
        results = detector.analyze(**data)

        print(f"\nStage 1 Detected: {results['stage_1_detected']}")
        print(f"\n{results['summary']}")

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have set ALPACA_API_KEY and ALPACA_SECRET_KEY!")
        print("Get free API keys at https://alpaca.markets/")

    print("\n" + "=" * 70)


def example_multiple_symbols():
    """
    Example: Fetch and analyze multiple symbols.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Multiple Symbols")
    print("=" * 70)

    symbols = ['AAPL', 'MSFT', 'TSLA', 'SPY']

    try:
        # Create fetcher (uses paper trading by default)
        fetcher = AlpacaDataFetcher(paper=True)

        print(f"\nFetching data for {len(symbols)} symbols...")
        all_data = fetcher.fetch_multiple_symbols(symbols, days=30)

        # Analyze each symbol
        detector = MarketStateDetector()

        for symbol, data in all_data.items():
            if data is None:
                print(f"\n{symbol}: Failed to fetch data")
                continue

            print(f"\n{symbol}:")
            print(f"  Retrieved {len(data['closes'])} bars")
            print(f"  Latest close: ${data['closes'][-1]:.2f}")

            results = detector.analyze(**data)
            print(f"  Stage 1 Detected: {results['stage_1_detected']}")

            if results['stage_1_detected']:
                print(f"  Signals: {results['flags']}")

    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 70)


def example_context_manager():
    """
    Example using context manager (recommended pattern).
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Using Context Manager")
    print("=" * 70)

    try:
        # Context manager pattern (recommended)
        with AlpacaDataFetcher(paper=True) as fetcher:
            print("\nFetching SPY data...")
            data = fetcher.fetch_daily_bars('SPY', days=30)

            print(f"Retrieved {len(data['closes'])} daily bars")

            # Analyze
            detector = MarketStateDetector()
            results = detector.analyze(**data)

            print(f"\nSPY Stage 1 Detected: {results['stage_1_detected']}")
            print(f"\n{results['summary']}")

    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 70)


def example_with_api_keys():
    """
    Example passing API keys directly (not using environment variables).
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Explicit API Keys")
    print("=" * 70)

    # Get keys from environment or use your own
    api_key = os.getenv('ALPACA_API_KEY', 'YOUR_API_KEY_HERE')
    secret_key = os.getenv('ALPACA_SECRET_KEY', 'YOUR_SECRET_KEY_HERE')

    if api_key == 'YOUR_API_KEY_HERE':
        print("\nSkipping this example - no API keys provided")
        print("Set ALPACA_API_KEY and ALPACA_SECRET_KEY to run this example")
        print("=" * 70)
        return

    try:
        # Pass keys directly
        fetcher = AlpacaDataFetcher(
            api_key=api_key,
            secret_key=secret_key,
            paper=True  # Use paper trading
        )

        print("\nFetching NVDA data...")
        data = fetcher.fetch_daily_bars('NVDA', days=30)

        print(f"Retrieved {len(data['closes'])} daily bars")

        # Analyze
        detector = MarketStateDetector()
        results = detector.analyze(**data)

        print(f"\nNVDA Stage 1 Detected: {results['stage_1_detected']}")

    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 70)


def example_paper_vs_live():
    """
    Example showing difference between paper and live endpoints.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Paper vs Live Trading")
    print("=" * 70)

    print("\nNote: Paper and live trading use different API keys!")
    print("Paper keys start with 'PK...' and 'PS...'")
    print("Live keys start with 'AK...' and 'AS...'")

    try:
        # Paper trading (default, safe for testing)
        print("\n1. Using paper trading endpoint:")
        with AlpacaDataFetcher(paper=True) as fetcher:
            data = fetcher.fetch_daily_bars('AAPL', days=5)
            print(f"   Retrieved {len(data['closes'])} bars from paper trading")

        # Live trading example (requires live API keys):
        # To test with live trading keys, create a separate script that sets
        # paper=False and uses your live API credentials instead of paper keys.
        # Note: Live and paper use the same data endpoint, but live keys are
        # required for actual trading operations.

    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 70)


def example_error_handling():
    """
    Example demonstrating error handling for invalid symbols.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Error Handling - Invalid Symbols")
    print("=" * 70)

    invalid_symbols = [
        'EUR/USD',    # Forex (not supported)
        'EURUSD',     # Forex (not supported)
        'ESH24',      # Futures (not supported)
        'INVALIDXYZ'  # Invalid stock
    ]

    fetcher = AlpacaDataFetcher(paper=True)

    for symbol in invalid_symbols:
        print(f"\nTrying to fetch {symbol}...")
        try:
            data = fetcher.fetch_daily_bars(symbol, days=10)
            print(f"  Success: Retrieved {len(data['closes'])} bars")
        except ValueError as e:
            print(f"  ValueError: {e}")
        except Exception as e:
            print(f"  Error: {e}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    print("\n")
    print("*" * 70)
    print("ALPACA MARKETS DATA INTEGRATION EXAMPLES")
    print("*" * 70)
    print("\nThese examples require:")
    print("  1. alpaca-py library installed (pip install alpaca-py)")
    print("  2. Alpaca API keys (free at https://alpaca.markets/)")
    print("  3. Environment variables set:")
    print("     export ALPACA_API_KEY='your_paper_key'")
    print("     export ALPACA_SECRET_KEY='your_paper_secret'")
    print("\nNote: Examples use paper trading by default (safe for testing)")
    print("*" * 70)
    print("\n")

    # Check if API keys are set
    if not os.getenv('ALPACA_API_KEY') or not os.getenv('ALPACA_SECRET_KEY'):
        print("WARNING: ALPACA_API_KEY and/or ALPACA_SECRET_KEY not set!")
        print("Examples will fail without API keys.")
        print("\nGet free API keys at: https://alpaca.markets/")
        print("\nThen set them:")
        print("  export ALPACA_API_KEY='your_key'")
        print("  export ALPACA_SECRET_KEY='your_secret'")
        print("\n" + "*" * 70)
        print("\n")
        exit(1)

    # Run examples
    example_simple_fetch()
    example_multiple_symbols()
    example_context_manager()
    example_with_api_keys()
    example_paper_vs_live()
    example_error_handling()

    print("\n")
    print("*" * 70)
    print("Examples completed!")
    print("*" * 70)
    print("\n")
