# Alpaca Markets Data Integration Guide

Complete guide for fetching market data from Alpaca Markets to use with the market state detector.

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Setup Instructions](#setup-instructions)
- [Usage Examples](#usage-examples)
- [Advanced Usage](#advanced-usage)
- [Common Issues](#common-issues)
- [Paper vs Live Trading](#paper-vs-live-trading)
- [Best Practices](#best-practices)
- [Limitations](#limitations)

---

## Overview

Alpaca Markets provides commission-free trading and market data for US equities. This integration allows you to fetch daily OHLC data from Alpaca and analyze it with the market state detector.

**Key Benefits:**
- ✓ Commission-free US equity trading
- ✓ Simple REST API (no gateway process needed)
- ✓ Free data for all US stocks
- ✓ Paper trading for safe testing
- ✓ Easy API key management

**Limitations:**
- ✗ US equities only (no forex, futures, or international stocks)
- ✗ Free tier has rate limits (200 requests/minute)

---

## Prerequisites

### 1. Install alpaca-py Library

```bash
pip install alpaca-py
```

Or add to your project's requirements:

```bash
# requirements.txt
alpaca-py>=0.17.0
```

### 2. Create Alpaca Account

1. Go to [https://alpaca.markets/](https://alpaca.markets/)
2. Sign up for a free account
3. Choose "Paper Trading" for testing (recommended)

### 3. Get API Keys

1. Log in to Alpaca dashboard
2. Navigate to "Your API Keys" section
3. Copy your API Key and Secret Key
4. Keep them secure (never commit to version control)

**Note:** Paper and live trading use different API keys!

---

## Quick Start

### Simplest Usage

```python
from market_state_detector import MarketStateDetector
from market_state_detector.alpaca_data import fetch_alpaca_data

# Set environment variables first:
# export ALPACA_API_KEY="your_paper_key"
# export ALPACA_SECRET_KEY="your_paper_secret"

# Fetch data (uses paper trading by default)
data = fetch_alpaca_data('AAPL', days=30)

# Analyze
detector = MarketStateDetector()
results = detector.analyze(**data)

print(f"Stage 1 Detected: {results['stage_1_detected']}")
```

---

## Setup Instructions

### Step 1: Set Environment Variables

**Option 1: Using .env File (Recommended)**

This is the easiest way to manage API keys per project:

1. Install python-dotenv:
   ```bash
   pip install python-dotenv
   ```

2. Copy the example file:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and add your real keys:
   ```bash
   ALPACA_API_KEY=your_paper_key_here
   ALPACA_SECRET_KEY=your_paper_secret_here
   ```

4. Load in your Python code:
   ```python
   from dotenv import load_dotenv
   load_dotenv()  # This loads .env file

   # Now use Alpaca as normal
   from market_state_detector.alpaca_data import fetch_alpaca_data
   data = fetch_alpaca_data('AAPL', days=30)
   ```

**Important:** `.env` is already in `.gitignore` so your keys won't be committed.

**Option 2: Shell Export (Global)**

**macOS/Linux:**
```bash
export ALPACA_API_KEY="your_api_key_here"
export ALPACA_SECRET_KEY="your_secret_key_here"
```

Add to `~/.zshrc` or `~/.bashrc` to make permanent:
```bash
echo 'export ALPACA_API_KEY="your_key"' >> ~/.zshrc
echo 'export ALPACA_SECRET_KEY="your_secret"' >> ~/.zshrc
source ~/.zshrc
```

**Windows (PowerShell):**
```powershell
$env:ALPACA_API_KEY="your_api_key_here"
$env:ALPACA_SECRET_KEY="your_secret_key_here"
```

### Step 2: Verify Connection

Run the connection test script:

```bash
python check_alpaca_connection.py
```

This will test:
- Library installation
- API key configuration
- Data fetching
- Full integration

---

## Usage Examples

### Example 1: Simple Fetch

```python
from market_state_detector import MarketStateDetector
from market_state_detector.alpaca_data import fetch_alpaca_data

# Fetch AAPL data
data = fetch_alpaca_data('AAPL', days=30, paper=True)

# Analyze
detector = MarketStateDetector()
results = detector.analyze(**data)

if results['stage_1_detected']:
    print("⚠️ HIGH UNCERTAINTY - Exercise caution")
    print(f"Signals: {results['flags']}")
else:
    print("✓ Normal market conditions")
```

### Example 2: Context Manager (Recommended)

```python
from market_state_detector import MarketStateDetector
from market_state_detector.alpaca_data import AlpacaDataFetcher

with AlpacaDataFetcher(paper=True) as fetcher:
    data = fetcher.fetch_daily_bars('SPY', days=30)

    detector = MarketStateDetector()
    results = detector.analyze(**data)

    print(f"SPY Stage 1: {results['stage_1_detected']}")
```

### Example 3: Multiple Symbols

```python
from market_state_detector import MarketStateDetector
from market_state_detector.alpaca_data import AlpacaDataFetcher

symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'SPY']

with AlpacaDataFetcher(paper=True) as fetcher:
    all_data = fetcher.fetch_multiple_symbols(symbols, days=30)

    detector = MarketStateDetector()

    for symbol, data in all_data.items():
        if data is None:
            print(f"{symbol}: Failed to fetch")
            continue

        results = detector.analyze(**data)
        status = "⚠️" if results['stage_1_detected'] else "✓"
        print(f"{status} {symbol}: Stage 1 = {results['stage_1_detected']}")
```

### Example 4: Passing API Keys Directly

```python
from market_state_detector.alpaca_data import AlpacaDataFetcher

# Pass keys directly (not using environment variables)
fetcher = AlpacaDataFetcher(
    api_key='your_api_key',
    secret_key='your_secret_key',
    paper=True
)

data = fetcher.fetch_daily_bars('NVDA', days=30)
```

---

## Advanced Usage

### Custom Date Range

```python
from datetime import datetime, timedelta
from market_state_detector.alpaca_data import AlpacaDataFetcher

end_date = datetime.now() - timedelta(days=7)  # One week ago

with AlpacaDataFetcher(paper=True) as fetcher:
    data = fetcher.fetch_daily_bars(
        symbol='AAPL',
        days=30,
        end_date=end_date
    )
```

### Error Handling

```python
from market_state_detector.alpaca_data import AlpacaDataFetcher

fetcher = AlpacaDataFetcher(paper=True)

try:
    data = fetcher.fetch_daily_bars('AAPL', days=30)
except ValueError as e:
    print(f"Data error: {e}")
    # Handle invalid symbol, no data available, etc.
except ImportError as e:
    print(f"Library error: {e}")
    # Handle missing alpaca-py library
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Monitoring Multiple Symbols

```python
import time
from datetime import datetime
from market_state_detector import MarketStateDetector
from market_state_detector.alpaca_data import AlpacaDataFetcher

def monitor_symbols(symbols, check_interval=3600):
    """Monitor symbols every hour."""
    detector = MarketStateDetector()

    while True:
        print(f"\n[{datetime.now()}] Checking market conditions...")

        with AlpacaDataFetcher(paper=True) as fetcher:
            for symbol in symbols:
                try:
                    data = fetcher.fetch_daily_bars(symbol, days=30)
                    results = detector.analyze(**data)

                    if results['stage_1_detected']:
                        print(f"⚠️  {symbol}: HIGH UNCERTAINTY")
                    else:
                        print(f"✓  {symbol}: Normal conditions")

                except Exception as e:
                    print(f"❌ {symbol}: Error - {e}")

        time.sleep(check_interval)

# Monitor watchlist
monitor_symbols(['SPY', 'AAPL', 'TSLA', 'NVDA'])
```

---

## Common Issues

### "ModuleNotFoundError: No module named 'alpaca'"

**Solution:** Install the library:
```bash
pip install alpaca-py
```

### "ValueError: API key and secret key are required"

**Cause:** API keys not set

**Solutions:**
1. Set environment variables:
   ```bash
   export ALPACA_API_KEY="your_key"
   export ALPACA_SECRET_KEY="your_secret"
   ```
2. Or pass keys directly to `AlpacaDataFetcher(api_key=..., secret_key=...)`

### "ValueError: Symbol 'EUR/USD' appears to be a forex pair"

**Cause:** Alpaca only supports US equities

**Solution:** Use valid US stock tickers like 'AAPL', 'MSFT', 'TSLA'

### "ValueError: No data returned for symbol"

**Possible causes:**
1. Invalid ticker symbol → Verify on Alpaca website
2. Newly listed stock with limited history → Try fewer days
3. Symbol delisted → Check if still trading
4. API rate limit exceeded → Add delays between requests

### Rate Limit Errors

**Cause:** Free tier allows 200 requests/minute

**Solutions:**
1. Add delays between requests:
   ```python
   import time
   for symbol in symbols:
       data = fetcher.fetch_daily_bars(symbol, days=30)
       time.sleep(0.5)  # 500ms delay
   ```
2. Fetch multiple symbols in one request using `fetch_multiple_symbols()`
3. Cache results to avoid repeated fetches
4. Consider paid plan for higher limits

---

## Paper vs Live Trading

### Paper Trading (Default)

**Recommended for:**
- Testing and development
- Learning the API
- Strategy development
- Risk-free experimentation

**API keys:**
- Start with `PK...` (paper key)
- Start with `PS...` (paper secret)

**Usage:**
```python
fetcher = AlpacaDataFetcher(paper=True)  # Default
```

### Live Trading

**Use for:**
- Production environments
- Real money trading
- Actual market data access

**API keys:**
- Start with `AK...` (live key)
- Start with `AS...` (live secret)

**Usage:**
```python
fetcher = AlpacaDataFetcher(paper=False)
```

**⚠️ Important:** Paper and live API keys are different! Make sure you're using the correct keys for your endpoint.

---

## Best Practices

### 1. Use Environment Variables

Never hardcode API keys in your code:

```python
# ✓ Good
fetcher = AlpacaDataFetcher()  # Uses env vars

# ✗ Bad
fetcher = AlpacaDataFetcher(api_key='PK123...', secret_key='PS456...')
```

### 2. Use Paper Trading for Development

Always test with paper trading first:

```python
# Development/testing
fetcher = AlpacaDataFetcher(paper=True)

# Production (only after thorough testing)
fetcher = AlpacaDataFetcher(paper=False)
```

### 3. Cache Data Locally

Avoid repeated API calls:

```python
import pickle
from pathlib import Path

cache_file = Path('data_cache.pkl')

if cache_file.exists():
    with open(cache_file, 'rb') as f:
        data = pickle.load(f)
else:
    data = fetch_alpaca_data('AAPL', days=30)
    with open(cache_file, 'wb') as f:
        pickle.dump(data, f)
```

### 4. Respect Rate Limits

Add delays for bulk operations:

```python
import time

for symbol in large_symbol_list:
    data = fetcher.fetch_daily_bars(symbol, days=30)
    time.sleep(0.5)  # Respect rate limits
```

### 5. Use Context Managers

Ensure proper resource handling:

```python
# ✓ Good - automatic cleanup
with AlpacaDataFetcher(paper=True) as fetcher:
    data = fetcher.fetch_daily_bars('AAPL', days=30)

# ✗ Unnecessary - Alpaca client doesn't need explicit cleanup,
# but context manager pattern is still recommended for consistency
```

### 6. Handle Errors Gracefully

Always wrap API calls in try/except:

```python
try:
    data = fetch_alpaca_data('AAPL', days=30)
except ValueError as e:
    logger.error(f"Invalid request: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

---

## Limitations

### Market Coverage

**Supported:**
- ✓ US stocks (NYSE, NASDAQ, AMEX)
- ✓ ETFs

**Not Supported:**
- ✗ Forex pairs
- ✗ Futures contracts
- ✗ Options (use IBKR for options)
- ✗ International stocks
- ✗ Crypto (use dedicated crypto APIs)

### Data Access

**Available:**
- ✓ Daily bars (OHLC)
- ✓ Historical data
- ✓ Real-time data (paid plans)

**Rate Limits:**
- Free tier: 200 requests/minute
- Paid plans: Higher limits

### Symbol Validation

The module automatically rejects non-US equity symbols:

```python
# These will raise ValueError:
fetch_alpaca_data('EUR/USD')   # Forex
fetch_alpaca_data('EURUSD')    # Forex
fetch_alpaca_data('ES')        # Futures

# These work:
fetch_alpaca_data('AAPL')      # US stock
fetch_alpaca_data('SPY')       # US ETF
```

---

## Additional Resources

- **Alpaca Documentation:** [https://alpaca.markets/docs/](https://alpaca.markets/docs/)
- **alpaca-py GitHub:** [https://github.com/alpacahq/alpaca-py](https://github.com/alpacahq/alpaca-py)
- **Quick Reference:** See [quick-reference/ALPACA_QUICK_REFERENCE.md](quick-reference/ALPACA_QUICK_REFERENCE.md)
- **Examples:** See `examples/alpaca_usage.py`
- **Connection Test:** Run `python check_alpaca_connection.py`

---

## Support

For issues specific to:
- **Alpaca API:** Contact Alpaca support
- **alpaca-py library:** Open issue on GitHub
- **market-state-detector integration:** Open issue in this repository

---

*Last updated: January 2026*
