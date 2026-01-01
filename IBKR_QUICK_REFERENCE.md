# IBKR Integration - Quick Reference

## Installation

```bash
# Core package
pip install -e .

# Optional IBKR support
pip install ib_insync
```

## Setup Checklist

- [ ] Install `ib_insync`
- [ ] Start TWS or IB Gateway
- [ ] Login to IBKR account (paper or live)
- [ ] Enable API in settings (File → Global Configuration → API → Settings)
- [ ] Check "Enable ActiveX and Socket Clients"
- [ ] Note your port number (7497 for TWS paper trading)
- [ ] Run `python check_ibkr_connection.py` to verify setup

## Quick Start

### One-Line Fetch

```python
from market_state_detector.ibkr_data import fetch_ibkr_data

data = fetch_ibkr_data('AAPL', days=30, port=7497)
```

### Analyze Immediately

```python
from market_state_detector import MarketStateDetector
from market_state_detector.ibkr_data import fetch_ibkr_data

data = fetch_ibkr_data('AAPL', days=30, port=7497)
detector = MarketStateDetector()
results = detector.analyze(**data)
```

### Multiple Symbols

```python
from market_state_detector.ibkr_data import IBKRDataFetcher

with IBKRDataFetcher(port=7497) as fetcher:
    data = fetcher.fetch_multiple_symbols(['AAPL', 'MSFT', 'GOOGL'])
```

## Port Numbers

| Setup | Port |
|-------|------|
| TWS Paper | 7497 |
| TWS Live | 7496 |
| Gateway Paper | 4002 |
| Gateway Live | 4001 |

## Common Errors

### "ModuleNotFoundError: No module named 'ib_insync'"
```bash
pip install ib_insync
```

### "ConnectionError: Failed to connect"
- Verify TWS/Gateway is running
- Check port number matches
- Ensure API connections enabled
- Try different client ID

### "ValueError: Could not find contract"
- Verify ticker symbol is correct
- Try exchange='SMART' for automatic routing
- Check symbol on IBKR website

## Data Format

Returned dictionary structure:
```python
{
    'opens': [100.0, 101.0, ...],
    'highs': [102.0, 103.0, ...],
    'lows': [98.0, 99.0, ...],
    'closes': [101.0, 102.0, ...]
}
```

All arrays same length, chronologically ordered (oldest first).

## Examples Location

- Basic usage: `examples/ibkr_usage.py`
- Connection test: `check_ibkr_connection.py`
- Full docs: `docs/IBKR_INTEGRATION.md`

## API Reference

### `fetch_ibkr_data(symbol, days=30, port=7497, **kwargs)`

Convenience function for single fetch.

**Parameters:**
- `symbol`: Ticker symbol (e.g., 'AAPL')
- `days`: Number of daily bars (default: 30)
- `port`: TWS/Gateway port
- `exchange`: Exchange code (default: 'SMART')
- `currency`: Currency (default: 'USD')

**Returns:** Dict with 'opens', 'highs', 'lows', 'closes'

### `IBKRDataFetcher(host, port, client_id)`

Main fetcher class for persistent connections.

**Methods:**
- `connect()`: Connect to TWS/Gateway
- `disconnect()`: Close connection
- `fetch_daily_bars(symbol, days)`: Get OHLC data
- `fetch_multiple_symbols(symbols)`: Batch fetch

**Context Manager:**
```python
with IBKRDataFetcher(port=7497) as fetcher:
    data = fetcher.fetch_daily_bars('AAPL', days=30)
```

## Best Practices

1. **Use context manager** for automatic connection handling
2. **Use paper trading** for testing
3. **Enable read-only API** to prevent accidental orders
4. **Cache data locally** to avoid repeated API calls
5. **Add retry logic** for production systems
6. **Respect rate limits** - add delays for bulk operations

## Security Types

```python
# Stocks (default)
data = fetcher.fetch_daily_bars('AAPL', days=30)

# Forex
data = fetcher.fetch_daily_bars(
    'EUR', days=30,
    exchange='IDEALPRO',
    security_type='CASH'
)

# Futures
data = fetcher.fetch_daily_bars(
    'ES', days=30,
    exchange='GLOBEX',
    security_type='FUT'
)
```

## Support

- **IBKR docs:** https://interactivebrokers.github.io/tws-api/
- **ib_insync docs:** https://ib-insync.readthedocs.io/
- **This project:** See README.md and docs/IBKR_INTEGRATION.md

## Troubleshooting Script

```bash
python check_ibkr_connection.py
```

Runs comprehensive tests and provides detailed diagnostics.
