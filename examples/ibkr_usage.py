"""
Example: Using IBKR/CapTrader data with the market state detector.

This example demonstrates how to fetch daily OHLC data from Interactive Brokers
or CapTrader and analyze it with the MarketStateDetector.

Prerequisites:
    1. Install ib_insync: pip install ib_insync
    2. Have TWS (Trader Workstation) or IB Gateway running
    3. Enable API connections in TWS/Gateway settings:
       - Go to File -> Global Configuration -> API -> Settings
       - Check "Enable ActiveX and Socket Clients"
       - Set a port (7497 for paper trading, 7496 for live)
       - Add 127.0.0.1 to trusted IPs if needed
"""

from market_state_detector import MarketStateDetector

try:
    from market_state_detector.ibkr_data import IBKRDataFetcher, fetch_ibkr_data
except ImportError:
    print("ERROR: ib_insync library is not installed.")
    print("Install with: pip install ib_insync")
    exit(1)


def example_simple_fetch():
    """
    Simple example: Fetch data and analyze with convenience function.
    """
    print("=" * 70)
    print("EXAMPLE 1: Simple IBKR Data Fetch")
    print("=" * 70)

    try:
        # Fetch data using convenience function
        # This automatically connects and disconnects
        print("\nFetching 30 days of AAPL data from IBKR...")
        data = fetch_ibkr_data(
            symbol='AAPL',
            days=30,
            port=4001  # IB Gateway live trading (ändern zu 4002 für Demo, 7497 für TWS Demo)
        )

        print(f"Retrieved {len(data['closes'])} daily bars")
        print(f"Date range: ${data['closes'][0]:.2f} -> ${data['closes'][-1]:.2f}")

        # Analyze with detector
        detector = MarketStateDetector()
        results = detector.analyze(**data)

        print(f"\nStage 1 Detected: {results['stage_1_detected']}")
        print(f"\n{results['summary']}")

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure TWS/Gateway is running and API is enabled!")

    print("\n" + "=" * 70)


def example_persistent_connection():
    """
    Advanced example: Use persistent connection for multiple fetches.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Multiple Symbols with Persistent Connection")
    print("=" * 70)

    symbols = ['AAPL', 'MSFT', 'GOOGL']

    try:
        # Create fetcher and maintain connection
        fetcher = IBKRDataFetcher(
            host='127.0.0.1',
            port=4001,  # IB Gateway live trading
            client_id=1
        )

        print("\nConnecting to IBKR...")
        fetcher.connect()
        print("Connected successfully!")

        # Fetch multiple symbols
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

            results = detector.analyze(**data)
            print(f"  Stage 1 Detected: {results['stage_1_detected']}")

            if results['stage_1_detected']:
                print(f"  Signals: {results['flags']}")

        # Disconnect
        fetcher.disconnect()
        print("\nDisconnected from IBKR")

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure TWS/Gateway is running and API is enabled!")

    print("\n" + "=" * 70)


def example_context_manager():
    """
    Example using context manager for automatic connection handling.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Using Context Manager")
    print("=" * 70)

    try:
        # Context manager automatically connects and disconnects
        with IBKRDataFetcher(port=4001) as fetcher:
            print("\nFetching SPY data...")
            data = fetcher.fetch_daily_bars('SPY', days=30)

            print(f"Retrieved {len(data['closes'])} daily bars")

            # Analyze
            detector = MarketStateDetector()
            results = detector.analyze(**data)

            print(f"\nSPY Stage 1 Detected: {results['stage_1_detected']}")
            print(f"\n{results['summary']}")

        print("\nConnection closed automatically")

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure TWS/Gateway is running and API is enabled!")

    print("\n" + "=" * 70)


def example_custom_contract():
    """
    Example fetching data for different security types.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Custom Contract Types")
    print("=" * 70)

    try:
        with IBKRDataFetcher(port=4001) as fetcher:
            # Fetch EUR/USD forex data
            print("\nFetching EUR.USD forex data...")
            data = fetcher.fetch_daily_bars(
                symbol='EUR',
                days=30,
                exchange='IDEALPRO',
                currency='USD',
                security_type='CASH'
            )

            print(f"Retrieved {len(data['closes'])} daily bars")
            print(f"Latest rate: {data['closes'][-1]:.4f}")

            # Analyze
            detector = MarketStateDetector()
            results = detector.analyze(**data)

            print(f"\nStage 1 Detected: {results['stage_1_detected']}")

    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: Forex data may require different permissions")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    print("\n")
    print("*" * 70)
    print("IBKR/CapTrader Data Integration Examples")
    print("*" * 70)
    print("\nThese examples require:")
    print("  1. ib_insync library installed")
    print("  2. TWS or IB Gateway running")
    print("  3. API connections enabled")
    print("\n")

    # Run examples
    example_simple_fetch()

    # Uncomment to run additional examples:
    # example_persistent_connection()
    # example_context_manager()
    # example_custom_contract()

    print("\n")
    print("*" * 70)
    print("Examples completed!")
    print("*" * 70)
    print("\n")
