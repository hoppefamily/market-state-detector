#!/usr/bin/env python
"""
IBKR Connection Test Script

Run this script to verify that your IBKR/CapTrader setup is working correctly
before using the market state detector with live data.

Prerequisites:
    1. pip install ib_insync
    2. TWS or IB Gateway running
    3. API connections enabled in settings

Usage:
    python check_ibkr_connection.py
"""

import asyncio
import sys

# Fix for Python 3.10+ event loop requirement
if sys.version_info >= (3, 10):
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)


def check_imports():
    """Check that required libraries are available."""
    print("=" * 70)
    print("Step 1: Checking Python libraries...")
    print("=" * 70)

    try:
        import ib_insync
        print("✓ ib_insync library found")
        print(f"  Version: {ib_insync.__version__}")
    except ImportError:
        print("❌ ib_insync library NOT found")
        print("   Install with: pip install ib_insync")
        return False

    try:
        from market_state_detector.ibkr_data import IBKRDataFetcher
        print("✓ market_state_detector IBKR module found")
    except ImportError as e:
        print(f"❌ Failed to import IBKR module: {e}")
        return False

    print()
    return True


def test_connection(port=7497):
    """Test connection to TWS/Gateway."""
    print("=" * 70)
    print(f"Step 2: Testing connection to IBKR on port {port}...")
    print("=" * 70)

    from market_state_detector.ibkr_data import IBKRDataFetcher

    try:
        fetcher = IBKRDataFetcher(port=port)
        print(f"Connecting to 127.0.0.1:{port}...")

        if fetcher.connect(timeout=5):
            print("✓ Successfully connected to IBKR!")

            # Check connection details
            if fetcher.ib and fetcher.ib.client:
                print(f"  Server version: {fetcher.ib.client.serverVersion()}")
                print(f"  Connection time: {fetcher.ib.client.connTime()}")

            fetcher.disconnect()
            print("✓ Disconnected successfully")
            print()
            return True

    except ConnectionError as e:
        print(f"❌ Connection failed: {e}")
        print()
        print("Troubleshooting tips:")
        print("  1. Make sure TWS or IB Gateway is running")
        print("  2. Check that the port number is correct:")
        print("     - TWS Paper: 7497")
        print("     - TWS Live: 7496")
        print("     - Gateway Paper: 4002")
        print("     - Gateway Live: 4001")
        print("  3. Verify API settings (File → Global Configuration → API → Settings):")
        print("     - 'Enable ActiveX and Socket Clients' must be checked")
        print("     - Check the socket port number matches")
        print("  4. Try different client ID (currently using 1)")
        print()
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print()
        return False


def test_data_fetch():
    """Test fetching actual market data."""
    print("=" * 70)
    print("Step 3: Testing data fetch for AAPL...")
    print("=" * 70)

    from market_state_detector.ibkr_data import fetch_ibkr_data

    try:
        print("Fetching 10 days of AAPL data...")
        data = fetch_ibkr_data('AAPL', days=10, port=7497)

        print(f"✓ Successfully retrieved {len(data['closes'])} daily bars")
        print(f"  Latest close: ${data['closes'][-1]:.2f}")
        print(f"  Data keys: {list(data.keys())}")
        print(f"  All arrays same length: {len(set(len(v) for v in data.values())) == 1}")
        print()
        return True

    except Exception as e:
        print(f"❌ Data fetch failed: {e}")
        print()
        print("Possible issues:")
        print("  1. Symbol 'AAPL' not found (unlikely)")
        print("  2. No market data subscription for stocks")
        print("  3. Connection lost during fetch")
        print("  4. Insufficient historical data")
        print()
        return False


def test_full_integration():
    """Test full integration with market state detector."""
    print("=" * 70)
    print("Step 4: Testing full integration with detector...")
    print("=" * 70)

    try:
        from market_state_detector import MarketStateDetector
        from market_state_detector.ibkr_data import fetch_ibkr_data

        print("Fetching SPY data and analyzing...")
        data = fetch_ibkr_data('SPY', days=30, port=7497)

        detector = MarketStateDetector()
        results = detector.analyze(**data)

        print("✓ Analysis completed successfully")
        print(f"  Stage 1 detected: {results['stage_1_detected']}")
        print(f"  Signals checked: {list(results['signals'].keys())}")
        print()
        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        print()
        return False


def main():
    """Run all tests."""
    print("\n")
    print("*" * 70)
    print("IBKR CONNECTION TEST")
    print("*" * 70)
    print()

    # Get port from user
    print("Which port is your TWS/Gateway using?")
    print("  1. 7497 (TWS Paper Trading) [default]")
    print("  2. 7496 (TWS Live Trading)")
    print("  3. 4002 (Gateway Paper Trading)")
    print("  4. 4001 (Gateway Live Trading)")
    print("  5. Custom port")
    print()

    choice = input("Enter choice (1-5) or press Enter for default: ").strip()

    port_map = {
        '1': 7497,
        '2': 7496,
        '3': 4002,
        '4': 4001,
        '': 7497  # default
    }

    if choice == '5':
        try:
            port = int(input("Enter custom port: "))
        except ValueError:
            print("Invalid port, using default 7497")
            port = 7497
    else:
        port = port_map.get(choice, 7497)

    print(f"\nUsing port: {port}")
    print()

    # Run tests
    results = []

    results.append(("Import check", check_imports()))

    if results[0][1]:  # Only continue if imports worked
        results.append(("Connection test", test_connection(port)))

        if results[1][1]:  # Only continue if connection worked
            results.append(("Data fetch test", test_data_fetch()))

            if results[2][1]:  # Only continue if data fetch worked
                results.append(("Integration test", test_full_integration()))

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False

    print()

    if all_passed:
        print("🎉 All tests passed! Your IBKR setup is working correctly.")
        print()
        print("You can now use IBKR data fetching with market-state-detector:")
        print()
        print("    from market_state_detector import MarketStateDetector")
        print("    from market_state_detector.ibkr_data import fetch_ibkr_data")
        print()
        print("    data = fetch_ibkr_data('AAPL', days=30, port={})".format(port))
        print("    detector = MarketStateDetector()")
        print("    results = detector.analyze(**data)")
        print()
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        print()
        print("Common solutions:")
        print("  - Make sure TWS/Gateway is running and logged in")
        print("  - Verify API settings are enabled")
        print("  - Check firewall settings")
        print("  - Try restarting TWS/Gateway")
        print()

    print("*" * 70)
    print()

    return 0 if all_passed else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
