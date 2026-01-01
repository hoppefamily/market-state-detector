# IBKR/CapTrader Data Integration Guide

This guide explains how to use the optional IBKR data fetching functionality with market-state-detector.

## Overview

The `ibkr_data` module provides seamless integration with Interactive Brokers (IBKR) and CapTrader APIs to fetch daily OHLC data that can be directly analyzed by the MarketStateDetector. This is an **optional** component - the core detector functionality works with data from any source.

## Requirements

### 1. Install ib_insync Library

```bash
pip install ib_insync
```

This library provides a clean Python interface to IBKR's TWS API.

### 2. Install and Configure TWS or IB Gateway

**Option A: Trader Workstation (TWS)**
- Download from [Interactive Brokers](https://www.interactivebrokers.com/en/trading/tws.php)
- Full-featured trading platform with charting and analysis tools
- Larger memory footprint

**Option B: IB Gateway** (Recommended for automated data fetching)
- Download from [Interactive Brokers](https://www.interactivebrokers.com/en/trading/ibgateway-stable.php)
- Lightweight server for API connections
- Smaller memory footprint, ideal for headless systems

### 3. Enable API Connections

In TWS/Gateway:
1. Go to **File → Global Configuration → API → Settings**
2. Check **"Enable ActiveX and Socket Clients"**
3. Note the **Socket port** number:
   - Default for TWS paper trading: `7497`
   - Default for TWS live trading: `7496`
   - Default for Gateway paper trading: `4002`
   - Default for Gateway live trading: `4001`
4. If needed, add `127.0.0.1` to **Trusted IP Addresses**
5. Consider checking **"Read-Only API"** for safety (prevents order placement)

### 4. Login to Your Account

Start TWS/Gateway and login with your IBKR credentials (paper or live account).

## Basic Usage

### Simple One-Time Fetch

```python
from market_state_detector import MarketStateDetector
from market_state_detector.ibkr_data import fetch_ibkr_data

# Fetch 30 days of AAPL data
data = fetch_ibkr_data('AAPL', days=30, port=7497)

# Analyze with detector
detector = MarketStateDetector()
results = detector.analyze(**data)

print(f"Stage 1 Detected: {results['stage_1_detected']}")
```

### Persistent Connection for Multiple Fetches

```python
from market_state_detector import MarketStateDetector
from market_state_detector.ibkr_data import IBKRDataFetcher

# Create fetcher with persistent connection
fetcher = IBKRDataFetcher(
    host='127.0.0.1',
    port=7497,
    client_id=1
)

# Connect once
fetcher.connect()

# Fetch multiple symbols efficiently
symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
detector = MarketStateDetector()

for symbol in symbols:
    data = fetcher.fetch_daily_bars(symbol, days=30)
    results = detector.analyze(**data)
    print(f"{symbol}: Stage 1 = {results['stage_1_detected']}")

# Disconnect when done
fetcher.disconnect()
```

### Using Context Manager (Recommended)

```python
from market_state_detector import MarketStateDetector
from market_state_detector.ibkr_data import IBKRDataFetcher

# Connection automatically managed
with IBKRDataFetcher(port=7497) as fetcher:
    data = fetcher.fetch_daily_bars('SPY', days=30)

    detector = MarketStateDetector()
    results = detector.analyze(**data)

    print(results['summary'])
# Automatically disconnects here
```

## Advanced Usage

### Custom Security Types

Fetch data for different security types beyond stocks:

```python
from market_state_detector.ibkr_data import IBKRDataFetcher

with IBKRDataFetcher(port=7497) as fetcher:
    # Forex (EUR/USD)
    forex_data = fetcher.fetch_daily_bars(
        symbol='EUR',
        days=30,
        exchange='IDEALPRO',
        currency='USD',
        security_type='CASH'
    )

    # Index (S&P 500)
    index_data = fetcher.fetch_daily_bars(
        symbol='SPX',
        days=30,
        exchange='CBOE',
        currency='USD',
        security_type='IND'
    )
```

### Multiple Symbols in One Call

```python
from market_state_detector.ibkr_data import IBKRDataFetcher

with IBKRDataFetcher(port=7497) as fetcher:
    # Fetch multiple symbols at once
    all_data = fetcher.fetch_multiple_symbols(
        symbols=['AAPL', 'MSFT', 'GOOGL'],
        days=30
    )

    # Process each symbol
    for symbol, data in all_data.items():
        if data is None:
            print(f"{symbol}: Failed to fetch")
            continue

        detector = MarketStateDetector()
        results = detector.analyze(**data)
        print(f"{symbol}: Stage 1 = {results['stage_1_detected']}")
```

### Custom Date Range

```python
from datetime import datetime, timedelta
from market_state_detector.ibkr_data import IBKRDataFetcher

with IBKRDataFetcher(port=7497) as fetcher:
    # Fetch data ending 7 days ago
    end_date = datetime.now() - timedelta(days=7)

    data = fetcher.fetch_daily_bars(
        symbol='AAPL',
        days=30,
        end_date=end_date
    )
```

## Port Configuration

Choose the correct port based on your setup:

| TWS/Gateway | Account Type | Port |
|------------|--------------|------|
| TWS        | Paper        | 7497 |
| TWS        | Live         | 7496 |
| IB Gateway | Paper        | 4002 |
| IB Gateway | Live         | 4001 |

Example for live trading with IB Gateway:

```python
from market_state_detector.ibkr_data import fetch_ibkr_data

data = fetch_ibkr_data('AAPL', days=30, port=4001)  # Live account
```

## Error Handling

The module provides clear error messages for common issues:

```python
from market_state_detector.ibkr_data import IBKRDataFetcher

try:
    with IBKRDataFetcher(port=7497) as fetcher:
        data = fetcher.fetch_daily_bars('INVALIDTICKER', days=30)
except ConnectionError as e:
    print(f"Connection failed: {e}")
    print("Make sure TWS/Gateway is running!")
except ValueError as e:
    print(f"Data fetch failed: {e}")
    print("Check that the symbol is valid")
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install ib_insync")
```

## Common Issues

### "ModuleNotFoundError: No module named 'ib_insync'"

**Solution:** Install the library:
```bash
pip install ib_insync
```

### "ConnectionError: Failed to connect to IBKR"

**Possible causes:**
1. TWS/Gateway is not running → Start TWS/Gateway
2. Wrong port number → Check your port in TWS/Gateway settings
3. API connections disabled → Enable in Global Configuration
4. Client ID conflict → Try a different `client_id` (1-32)

### "ValueError: Could not find contract for symbol"

**Possible causes:**
1. Invalid ticker symbol → Verify symbol on IBKR website
2. Wrong exchange → Try 'SMART' exchange for automatic routing
3. Symbol requires specific exchange → Research correct exchange code

### "No data returned for symbol"

**Possible causes:**
1. Symbol has no trading history → Check if recently listed
2. Requesting too much history → IBKR has data limits
3. Market closed/holiday → Try end_date from a trading day

## Best Practices

### 1. Use Read-Only API Mode

For data fetching only, enable read-only mode in TWS/Gateway settings to prevent accidental order placement.

### 2. Use Paper Trading Account

For testing and development, use a paper trading account to avoid any risk.

### 3. Implement Retry Logic

Network issues can occur; implement retry logic for production:

```python
import time
from market_state_detector.ibkr_data import IBKRDataFetcher

def fetch_with_retry(symbol, days=30, max_retries=3):
    for attempt in range(max_retries):
        try:
            with IBKRDataFetcher(port=7497) as fetcher:
                return fetcher.fetch_daily_bars(symbol, days=days)
        except ConnectionError as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(2)
            else:
                raise
```

### 4. Cache Data Locally

Avoid repeated API calls by caching data:

```python
import json
from datetime import date

def cache_data(symbol, data):
    filename = f"cache/{symbol}_{date.today()}.json"
    with open(filename, 'w') as f:
        json.dump(data, f)

def load_cached_data(symbol):
    filename = f"cache/{symbol}_{date.today()}.json"
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
```

### 5. Respect Rate Limits

IBKR has rate limits on historical data requests. For bulk operations:
- Add small delays between requests
- Use `fetch_multiple_symbols()` which handles this internally
- Consider caching data

## Integration with Existing Workflows

### CSV Export for CLI Tool

```python
import csv
from market_state_detector.ibkr_data import fetch_ibkr_data

# Fetch data from IBKR
data = fetch_ibkr_data('AAPL', days=30, port=7497)

# Export to CSV for use with CLI tool
with open('aapl_data.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['open', 'high', 'low', 'close'])

    for i in range(len(data['closes'])):
        writer.writerow([
            data['opens'][i],
            data['highs'][i],
            data['lows'][i],
            data['closes'][i]
        ])

# Now use with CLI
# market-state-detector --csv aapl_data.csv
```

### Automated Monitoring Script

```python
import time
from datetime import datetime
from market_state_detector import MarketStateDetector
from market_state_detector.ibkr_data import IBKRDataFetcher

def monitor_symbols(symbols, check_interval=3600):
    """Monitor symbols every hour."""
    detector = MarketStateDetector()

    while True:
        print(f"\n[{datetime.now()}] Checking market conditions...")

        with IBKRDataFetcher(port=7497) as fetcher:
            for symbol in symbols:
                try:
                    data = fetcher.fetch_daily_bars(symbol, days=30)
                    results = detector.analyze(**data)

                    if results['stage_1_detected']:
                        print(f"⚠️  {symbol}: HIGH UNCERTAINTY - {results['flags']}")
                    else:
                        print(f"✓  {symbol}: Normal conditions")

                except Exception as e:
                    print(f"❌ {symbol}: Error - {e}")

        print(f"Next check in {check_interval} seconds...")
        time.sleep(check_interval)

# Monitor portfolio
monitor_symbols(['SPY', 'AAPL', 'MSFT'])
```

## Additional Resources

- [IBKR API Documentation](https://interactivebrokers.github.io/tws-api/)
- [ib_insync Documentation](https://ib-insync.readthedocs.io/)
- [Market State Detector README](../README.md)
- [Example Scripts](../examples/ibkr_usage.py)

## Support

For issues specific to:
- **IBKR data fetching**: Check this guide and ib_insync documentation
- **Market state detection**: See main [README.md](../README.md)
- **IBKR platform/account**: Contact Interactive Brokers support
