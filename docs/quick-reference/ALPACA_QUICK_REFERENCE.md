# Alpaca Integration - Quick Reference

Essential commands and patterns for using Alpaca Markets data with market-state-detector.

---

## Installation

```bash
pip install alpaca-py
```

Or install with optional dependency:
```bash
pip install -e ".[alpaca]"
```

---

## Setup

### Get API Keys

1. Sign up at [https://alpaca.markets/](https://alpaca.markets/)
2. Get API keys from dashboard
3. Use paper trading keys for testing (recommended)

### Set Environment Variables

**Option 1: Using .env file (Recommended)**

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your real keys
# ALPACA_API_KEY=your_paper_key_here
# ALPACA_SECRET_KEY=your_paper_secret_here
```

Then in your Python code:
```python
from dotenv import load_dotenv
load_dotenv()  # Load .env file

# Now use Alpaca as normal
from market_state_detector.alpaca_data import fetch_alpaca_data
data = fetch_alpaca_data('AAPL', days=30)
```

**Option 2: Shell export**

```bash
export ALPACA_API_KEY="your_paper_key"
export ALPACA_SECRET_KEY="your_paper_secret"
```

---

## Quick Start

### One-Line Fetch

```python
from market_state_detector.alpaca_data import fetch_alpaca_data

data = fetch_alpaca_data('AAPL', days=30, paper=True)
```

### Analyze Immediately

```python
from market_state_detector import MarketStateDetector
from market_state_detector.alpaca_data import fetch_alpaca_data

data = fetch_alpaca_data('AAPL', days=30)
detector = MarketStateDetector()
results = detector.analyze(**data)
```

### Multiple Symbols

```python
from market_state_detector.alpaca_data import AlpacaDataFetcher

with AlpacaDataFetcher(paper=True) as fetcher:
    data = fetcher.fetch_multiple_symbols(['AAPL', 'MSFT', 'GOOGL'])
```

---

## API Key Types

| Key Type | Prefix | Endpoint | Use Case |
|----------|--------|----------|----------|
| Paper API Key | `PK...` | Paper trading | Testing, development |
| Paper Secret | `PS...` | Paper trading | Testing, development |
| Live API Key | `AK...` | Live trading | Production, real money |
| Live Secret | `AS...` | Live trading | Production, real money |

**⚠️ Important:** Paper and live keys are different! Make sure you're using the correct ones.

---

## Common Patterns

### Pattern 1: Environment Variables (Recommended)

```python
from market_state_detector.alpaca_data import AlpacaDataFetcher

# Uses ALPACA_API_KEY and ALPACA_SECRET_KEY env vars
fetcher = AlpacaDataFetcher(paper=True)
data = fetcher.fetch_daily_bars('AAPL', days=30)
```

### Pattern 2: Explicit Keys

```python
from market_state_detector.alpaca_data import AlpacaDataFetcher

fetcher = AlpacaDataFetcher(
    api_key='your_key',
    secret_key='your_secret',
    paper=True
)
data = fetcher.fetch_daily_bars('AAPL', days=30)
```

### Pattern 3: Context Manager

```python
from market_state_detector.alpaca_data import AlpacaDataFetcher

with AlpacaDataFetcher(paper=True) as fetcher:
    data = fetcher.fetch_daily_bars('SPY', days=30)
    # Process data
```

### Pattern 4: Convenience Function

```python
from market_state_detector.alpaca_data import fetch_alpaca_data

data = fetch_alpaca_data('AAPL', days=30, paper=True)
```

---

## Class: AlpacaDataFetcher

### Constructor

```python
AlpacaDataFetcher(
    api_key=None,        # Or use ALPACA_API_KEY env var
    secret_key=None,     # Or use ALPACA_SECRET_KEY env var
    paper=True           # Use paper trading (recommended)
)
```

### Methods

#### fetch_daily_bars()

```python
data = fetcher.fetch_daily_bars(
    symbol='AAPL',       # US equity ticker
    days=30,             # Number of days to fetch
    end_date=None        # Optional end date (default: today)
)

# Returns:
# {
#     'opens': [float, ...],
#     'highs': [float, ...],
#     'lows': [float, ...],
#     'closes': [float, ...]
# }
```

#### fetch_multiple_symbols()

```python
all_data = fetcher.fetch_multiple_symbols(
    symbols=['AAPL', 'MSFT', 'GOOGL'],
    days=30,
    end_date=None
)

# Returns: dict mapping symbol -> OHLC data
# Failed fetches have None as value
```

---

## Function: fetch_alpaca_data()

Convenience function for one-time fetches:

```python
from market_state_detector.alpaca_data import fetch_alpaca_data

data = fetch_alpaca_data(
    symbol='AAPL',
    days=30,
    api_key=None,      # Optional
    secret_key=None,   # Optional
    paper=True         # Use paper trading
)
```

---

## Supported Symbols

### ✓ Supported
- US stocks: `AAPL`, `MSFT`, `GOOGL`, `TSLA`
- ETFs: `SPY`, `QQQ`, `IWM`, `DIA`

### ✗ Not Supported
- Forex: `EUR/USD`, `EURUSD`
- Futures: `ES`, `CL`, `GC`
- Options: Use IBKR for options
- International stocks: Use IBKR for international

**Symbol validation:** The module automatically rejects non-US equity symbols.

---

## Error Handling

### Common Errors

```python
from market_state_detector.alpaca_data import AlpacaDataFetcher

fetcher = AlpacaDataFetcher(paper=True)

try:
    data = fetcher.fetch_daily_bars('AAPL', days=30)
except ValueError as e:
    # Invalid symbol, no data, or validation error
    print(f"Data error: {e}")
except ImportError as e:
    # alpaca-py not installed
    print(f"Library error: {e}")
```

### Validation Errors

```python
# These raise ValueError:
fetch_alpaca_data('EUR/USD')    # "appears to be a forex pair"
fetch_alpaca_data('EURUSD')     # "appears to be a forex pair"
fetch_alpaca_data('ES22')       # "appears to be a futures contract"

# These work:
fetch_alpaca_data('AAPL')       # ✓
fetch_alpaca_data('SPY')        # ✓
```

---

## Testing Connection

Run the connection test script:

```bash
python check_alpaca_connection.py
```

Tests:
1. Library installation
2. API key configuration
3. Connection to Alpaca
4. Data fetching
5. Symbol validation
6. Full integration

---

## Rate Limits

| Plan | Requests per Minute |
|------|-------------------|
| Free | 200 |
| Paid | Higher limits |

**Tip:** Add delays for bulk operations:

```python
import time

for symbol in symbols:
    data = fetcher.fetch_daily_bars(symbol, days=30)
    time.sleep(0.5)  # 500ms delay
```

---

## Complete Example

```python
from market_state_detector import MarketStateDetector
from market_state_detector.alpaca_data import AlpacaDataFetcher

# Watchlist
symbols = ['SPY', 'AAPL', 'MSFT', 'GOOGL', 'TSLA']

# Fetch and analyze
with AlpacaDataFetcher(paper=True) as fetcher:
    all_data = fetcher.fetch_multiple_symbols(symbols, days=30)

    detector = MarketStateDetector()

    for symbol, data in all_data.items():
        if data is None:
            print(f"{symbol}: Data fetch failed")
            continue

        results = detector.analyze(**data)

        if results['stage_1_detected']:
            print(f"⚠️  {symbol}: HIGH UNCERTAINTY - {results['flags']}")
        else:
            print(f"✓  {symbol}: Normal conditions")
```

---

## Best Practices

1. **Use environment variables** for API keys
2. **Use paper trading** for development and testing
3. **Cache results** to avoid repeated API calls
4. **Add delays** for bulk operations (rate limits)
5. **Handle errors** gracefully
6. **Validate symbols** before fetching (automatic)

---

## Comparison with IBKR

| Feature | Alpaca | IBKR |
|---------|--------|------|
| **US Stocks** | ✓ | ✓ |
| **Forex** | ✗ | ✓ |
| **Futures** | ✗ | ✓ |
| **Options** | ✗ | ✓ |
| **International** | ✗ | ✓ |
| **Commission** | Free | Varies |
| **Setup** | Simple (API keys) | Complex (Gateway) |
| **Rate Limits** | 200/min (free) | Higher |
| **Paper Trading** | Built-in | Separate account |

**Recommendation:**
- **Alpaca:** US stocks only, simple setup, free
- **IBKR:** All markets, complex setup, more features

---

## Resources

- **Full Guide:** [docs/ALPACA_INTEGRATION.md](../ALPACA_INTEGRATION.md)
- **Examples:** [examples/alpaca_usage.py](../../examples/alpaca_usage.py)
- **Connection Test:** [check_alpaca_connection.py](../../check_alpaca_connection.py)
- **Alpaca Docs:** [https://alpaca.markets/docs/](https://alpaca.markets/docs/)
- **alpaca-py GitHub:** [https://github.com/alpacahq/alpaca-py](https://github.com/alpacahq/alpaca-py)

---

## Troubleshooting

### Import Error

```
ImportError: alpaca-py library is required
```

**Solution:**
```bash
pip install alpaca-py
```

### API Key Error

```
ValueError: API key and secret key are required
```

**Solution:**
```bash
export ALPACA_API_KEY="your_key"
export ALPACA_SECRET_KEY="your_secret"
```

### Symbol Validation Error

```
ValueError: Symbol 'EUR/USD' appears to be a forex pair
```

**Solution:** Use valid US stock tickers like `AAPL`, `MSFT`, `SPY`

### No Data Error

```
ValueError: No data returned for symbol
```

**Possible causes:**
1. Invalid ticker symbol
2. Newly listed stock (try fewer days)
3. Delisted stock
4. Rate limit exceeded (add delays)

---

*Quick reference for Alpaca Markets integration with market-state-detector*
