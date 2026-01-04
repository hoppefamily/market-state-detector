#!/usr/bin/env python
"""
Alpaca Connection Test Script

Run this script to verify that your Alpaca Markets setup is working correctly
before using the market state detector with live data.

Prerequisites:
    1. pip install alpaca-py
    2. Alpaca account (free at https://alpaca.markets/)
    3. API keys from Alpaca dashboard
    4. Set environment variables:
       export ALPACA_API_KEY="your_key"
       export ALPACA_SECRET_KEY="your_secret"

Usage:
    python check_alpaca_connection.py
"""

import os
import sys


def check_imports():
    """Check that required libraries are available."""
    print("=" * 70)
    print("Step 1: Checking Python libraries...")
    print("=" * 70)

    try:
        import alpaca
        print("✓ alpaca-py library found")
        try:
            print(f"  Version: {alpaca.__version__}")
        except AttributeError:
            print("  Version: (version info not available)")
    except ImportError:
        print("❌ alpaca-py library NOT found")
        print("   Install with: pip install alpaca-py")
        return False

    try:
        from market_state_detector.alpaca_data import AlpacaDataFetcher
        print("✓ market_state_detector Alpaca module found")
    except ImportError as e:
        print(f"❌ Failed to import Alpaca module: {e}")
        return False

    print()
    return True


def check_api_keys():
    """Check that API keys are configured."""
    print("=" * 70)
    print("Step 2: Checking API keys...")
    print("=" * 70)

    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')

    if not api_key:
        print("❌ ALPACA_API_KEY environment variable not set")
        print()
        print("Set it with:")
        print("  export ALPACA_API_KEY='your_api_key'")
        print()
        return False
    else:
        # Show partial key for verification
        if len(api_key) > 8:
            masked = api_key[:4] + "..." + api_key[-4:]
        else:
            masked = "***"
        print(f"✓ ALPACA_API_KEY found: {masked}")

    if not secret_key:
        print("❌ ALPACA_SECRET_KEY environment variable not set")
        print()
        print("Set it with:")
        print("  export ALPACA_SECRET_KEY='your_secret_key'")
        print()
        return False
    else:
        # Show partial key for verification
        if len(secret_key) > 8:
            masked = secret_key[:4] + "..." + secret_key[-4:]
        else:
            masked = "***"
        print(f"✓ ALPACA_SECRET_KEY found: {masked}")

    # Check if keys look like paper or live keys
    if api_key.startswith('PK'):
        print("  Key type: Paper trading (recommended for testing)")
    elif api_key.startswith('AK'):
        print("  Key type: Live trading")
    else:
        print("  Key type: Unknown format")

    print()
    return True


def test_connection():
    """Test connection to Alpaca API."""
    print("=" * 70)
    print("Step 3: Testing connection to Alpaca...")
    print("=" * 70)

    from market_state_detector.alpaca_data import AlpacaDataFetcher

    try:
        print("Initializing Alpaca client...")
        AlpacaDataFetcher(paper=True)
        print("✓ Alpaca client initialized successfully")
        print("  Endpoint: Paper trading (safe for testing)")
        print()
        return True

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print()
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print()
        return False


def test_data_fetch():
    """Test fetching actual market data."""
    print("=" * 70)
    print("Step 4: Testing data fetch for AAPL...")
    print("=" * 70)

    from market_state_detector.alpaca_data import fetch_alpaca_data

    try:
        print("Fetching 10 days of AAPL data...")
        data = fetch_alpaca_data('AAPL', days=10, paper=True)

        print(f"✓ Successfully retrieved {len(data['closes'])} daily bars")
        print(f"  Latest close: ${data['closes'][-1]:.2f}")
        print(f"  Data keys: {list(data.keys())}")
        print(f"  All arrays same length: {len(set(len(v) for v in data.values())) == 1}")
        print()
        return True

    except ValueError as e:
        print(f"❌ Data fetch failed: {e}")
        print()
        print("Possible issues:")
        print("  1. Invalid API keys")
        print("  2. API rate limit exceeded (200 requests/minute for free tier)")
        print("  3. Network connection issue")
        print("  4. Alpaca API service issue")
        print()
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print()
        return False


def test_symbol_validation():
    """Test symbol validation (rejecting forex/futures)."""
    print("=" * 70)
    print("Step 5: Testing symbol validation...")
    print("=" * 70)

    from market_state_detector.alpaca_data import AlpacaDataFetcher

    test_cases = [
        ('AAPL', True, 'US equity'),
        ('EUR/USD', False, 'Forex pair'),
        ('EURUSD', False, 'Forex pair'),
    ]

    fetcher = AlpacaDataFetcher(paper=True)
    all_passed = True

    for symbol, should_succeed, description in test_cases:
        try:
            print(f"\nTesting {symbol} ({description})...")
            data = fetcher.fetch_daily_bars(symbol, days=5)
            if should_succeed:
                print(f"  ✓ Correctly accepted - got {len(data['closes'])} bars")
            else:
                print("  ❌ Should have been rejected but succeeded")
                all_passed = False
        except ValueError as e:
            if not should_succeed:
                print(f"  ✓ Correctly rejected: {str(e)[:60]}...")
            else:
                print(f"  ❌ Should have succeeded but was rejected: {e}")
                all_passed = False
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
            all_passed = False

    print()
    if all_passed:
        print("✓ All validation tests passed")
    else:
        print("❌ Some validation tests failed")

    print()
    return all_passed


def test_full_integration():
    """Test full integration with market state detector."""
    print("=" * 70)
    print("Step 6: Testing full integration with detector...")
    print("=" * 70)

    try:
        from market_state_detector import MarketStateDetector
        from market_state_detector.alpaca_data import fetch_alpaca_data

        print("Fetching SPY data and analyzing...")
        data = fetch_alpaca_data('SPY', days=30, paper=True)

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
    print("ALPACA CONNECTION TEST")
    print("*" * 70)
    print()
    print("This script will test your Alpaca setup in 6 steps.")
    print()

    # Run tests
    tests = [
        ("Import test", check_imports),
        ("API keys test", check_api_keys),
        ("Connection test", test_connection),
        ("Data fetch test", test_data_fetch),
        ("Symbol validation test", test_symbol_validation),
        ("Integration test", test_full_integration),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            if not result:
                print(f"Stopping after failed test: {test_name}")
                break
        except KeyboardInterrupt:
            print("\n\nTest interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error in {test_name}: {e}")
            results.append((test_name, False))
            break

    # Summary
    print()
    print("*" * 70)
    print("TEST SUMMARY")
    print("*" * 70)
    print()

    for test_name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"  {status}  {test_name}")

    all_passed = all(result for _, result in results)

    print()
    if all_passed:
        print("🎉 All tests passed! Your Alpaca setup is working correctly.")
        print()
        print("You can now use Alpaca data with market-state-detector:")
        print()
        print("  from market_state_detector import MarketStateDetector")
        print("  from market_state_detector.alpaca_data import fetch_alpaca_data")
        print()
        print("  data = fetch_alpaca_data('AAPL', days=30)")
        print("  detector = MarketStateDetector()")
        print("  results = detector.analyze(**data)")
        print()
    else:
        print("❌ Some tests failed. Please fix the issues above and try again.")
        print()
        print("Common issues:")
        print("  1. alpaca-py not installed: pip install alpaca-py")
        print("  2. API keys not set: export ALPACA_API_KEY and ALPACA_SECRET_KEY")
        print("  3. Invalid API keys: check your Alpaca dashboard")
        print("  4. Network connection issues")
        print()
        print("Get free API keys at: https://alpaca.markets/")
        print()

    print("*" * 70)
    print()


if __name__ == "__main__":
    main()
