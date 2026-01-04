# market-state-detector

A Python tool that detects high-uncertainty market regimes (Stage 1) using simple daily price behavior metrics. It automates manual checks that traders might perform to identify unstable market conditions and improve decision-making consistency.

**This is NOT a trading bot, NOT day trading, and NOT predictive.** It simply automates observable checks to help identify when market conditions may be too uncertain for normal operations.

## Features

- **Volatility Spike Detection**: Identifies abnormal volatility by comparing recent price movements to historical averages
- **Price Gap Detection**: Flags significant overnight gaps that may indicate market stress
- **Wide Range Detection**: Detects abnormally wide trading ranges suggesting increased uncertainty
- **Market Context Detection**: When Stage 1 triggers, compares against SPY/QQQ/DIA to classify conditions as broad market, sector-specific, or stock-specific
- **IBKR/CapTrader Integration**: Optional data fetching from Interactive Brokers (see [IBKR Integration Guide](docs/IBKR_INTEGRATION.md))
- **Alpaca Integration**: Optional data fetching from Alpaca (see [Alpaca Integration Guide](docs/ALPACA_INTEGRATION.md))
- **Modular Design**: Each detection method is independent and can be used separately
- **Config-Driven**: Easily customize detection thresholds via YAML configuration
- **CLI Support**: Command-line interface for analyzing CSV data files
- **Well Documented**: Clear docstrings and examples throughout

## Installation

```bash
# Clone the repository
git clone https://github.com/hoppefamily/market-state-detector.git
cd market-state-detector

# Install in development mode
pip install -e .

# Or install with dev dependencies for testing
pip install -e ".[dev]"

# Optional: Install IBKR data fetching support
pip install ib_insync
```

## Quick Start

### Daily Stock Checks (Recommended)

**The simplest way to use the detector** - check stocks before making trading decisions:

```bash
python check_stock.py SPY                 # Check market (Alpaca default)
python check_stock.py AAPL                # Check your positions
python check_stock.py TSLA --broker ibkr  # Use IBKR instead of Alpaca
python check_stock.py                     # Defaults to SPY
```

**Output example:**
```
============================================================
AAPL - MARKET STATE CHECK
============================================================

✓ No Stage 1 signals detected. Market behavior appears
  within normal parameters.

# (If Stage 1 triggers, you'll also see a market context message,
#  e.g. broad-market vs sector vs stock-specific.)

============================================================
```

**Requirements:**
- Alpaca (default): `pip install alpaca-py` + `ALPACA_API_KEY` / `ALPACA_SECRET_KEY` set (see [docs/quick-reference/ALPACA_QUICK_REFERENCE.md](docs/quick-reference/ALPACA_QUICK_REFERENCE.md))
- IBKR (`--broker ibkr`): IB Gateway or TWS running + `pip install ib_insync` + API connections enabled (see [IBKR Setup Guide](IBKR_SETUP_CHECKLIST.md))

**Exit codes:** 0 (normal), 1 (Stage 1 detected), 2 (error) - useful for scripting.

**Why this approach?** It matches the tool's philosophy: "consulted before making a decision." Quick, focused, daily.

---

### Testing IBKR Connection

Verify your TWS/Gateway setup:

```bash
python check_ibkr_connection.py
```

---

### Python API

```python
from market_state_detector import MarketStateDetector

# Sample closing prices (most recent last)
closing_prices = [100, 101, 100.5, 102, 101.5, ..., 120]  # spike at end

# Create detector and analyze
detector = MarketStateDetector()
results = detector.analyze(closing_prices)

# Check results
if results['stage_1_detected']:
    print(f"⚠️  High uncertainty detected!")
    print(f"Signals: {results['flags']}")
else:
    print("✓ Market conditions appear normal")
```

### Command Line

```bash
# Analyze data from CSV file
market-state-detector --csv examples/sample_data_with_spike.csv

# Use custom configuration
market-state-detector --csv data.csv --config custom_config.yaml

# Get JSON output for scripting
market-state-detector --csv data.csv --json
```

## Usage Examples

### Basic Usage (Closing Prices Only)

```python
from market_state_detector import MarketStateDetector

detector = MarketStateDetector()

# Minimum 21 data points required by default
closing_prices = [100.0, 101.0, ..., 120.0]

results = detector.analyze(closing_prices)
print(results['summary'])
```

### Full OHLC Analysis

```python
from market_state_detector import MarketStateDetector

detector = MarketStateDetector()

# Analyze with Open, High, Low, Close data
results = detector.analyze(
    closes=[100, 101, 102, ...],
    highs=[102, 103, 104, ...],
    lows=[98, 99, 100, ...],
    opens=[100, 101, 102, ...]
)

# Access individual signals
if results['signals']['volatility_spike']['detected']:
    details = results['signals']['volatility_spike']['details']
    print(f"Volatility spike: {details['spike_magnitude']:.2f}x threshold")
```

### IBKR/CapTrader Data Integration (Optional)

The package includes optional support for fetching daily OHLC data directly from Interactive Brokers or CapTrader:

```python
from market_state_detector import MarketStateDetector
from market_state_detector.ibkr_data import fetch_ibkr_data

# Fetch data from IBKR (requires ib_insync and TWS/Gateway running)
data = fetch_ibkr_data('AAPL', days=30, port=7497)

# Analyze directly
detector = MarketStateDetector()
results = detector.analyze(**data)
```

### Market Context (Optional)

If you pass a fetcher into `analyze_with_context()`, the detector will compare the stock's Stage 1 signals against SPY/QQQ/DIA to help explain whether the volatility looks market-wide, sector-specific, or stock-specific.

```python
from market_state_detector import MarketStateDetector
from market_state_detector.alpaca_data import AlpacaDataFetcher

with AlpacaDataFetcher(paper=True) as fetcher:
  data = fetcher.fetch_daily_bars('AAPL', days=30)

  detector = MarketStateDetector(symbol='AAPL')
  results = detector.analyze_with_context(symbol='AAPL', fetcher=fetcher, **data)

  print(results['summary'])
  if results.get('market_context'):
    print(results['market_context']['message'])
```

**Requirements for IBKR integration:**
1. Install ib_insync: `pip install ib_insync`
2. Have TWS (Trader Workstation) or IB Gateway running
3. Enable API connections in TWS/Gateway settings (File → Global Configuration → API → Settings)

**Port numbers:**
- `7497` - TWS paper trading
- `7496` - TWS live trading
- `4002` - IB Gateway paper trading
- `4001` - IB Gateway live trading

See [examples/ibkr_usage.py](examples/ibkr_usage.py) for more detailed examples including persistent connections and multiple symbols.

**Note:**
This project does not redistribute market data.
Users are responsible for ensuring compliance with their broker
and market data provider terms.

### Custom Configuration

```python
from market_state_detector import Config, MarketStateDetector

# Load custom config from YAML file
config = Config('custom_config.yaml')
detector = MarketStateDetector(config)

results = detector.analyze(closing_prices)
```

Example config file (`custom_config.yaml`):

```yaml
volatility:
  threshold_multiplier: 2.5  # More conservative (default: 2.0)
  lookback_period: 30         # Longer baseline (default: 20)

gaps:
  threshold_percent: 3.0      # Larger gaps only (default: 2.0)

ranges:
  threshold_percent: 75.0     # Much wider ranges (default: 50.0)
  lookback_period: 30
```

## Configuration Options

### Volatility Detection
- `threshold_multiplier`: How many times historical volatility to trigger (default: 2.0)
- `lookback_period`: Days to use for historical baseline (default: 20)

### Gap Detection
- `threshold_percent`: Minimum gap size as percentage (default: 2.0%)

### Range Detection
- `threshold_percent`: How much wider than average to trigger (default: 50%)
- `lookback_period`: Days to use for average range (default: 20)

### General
- `min_data_points`: Minimum data points required for analysis (default: 21)

## Project Structure

```
market-state-detector/
├── src/
│   └── market_state_detector/
│       ├── __init__.py          # Package initialization
│       ├── detector.py          # Main detector class
│       ├── config.py            # Configuration management
│       ├── volatility.py        # Volatility spike detection
│       ├── gaps.py              # Price gap detection
│       ├── ranges.py            # Wide range detection
│       ├── market_context.py     # Market context classification (SPY/QQQ/DIA)
│       ├── alpaca_data.py        # Optional Alpaca data fetching
│       ├── ibkr_data.py         # Optional IBKR data fetching
│       ├── cli.py               # Command-line interface
│       └── __main__.py          # Module entry point
├── check_stock.py                # Quick daily stock check script
├── tests/                       # Test suite
│   ├── test_detector.py
│   ├── test_volatility.py
│   ├── test_gaps.py
│   ├── test_ranges.py
│   ├── test_config.py
│   ├── test_market_context.py
│   └── conftest.py
├── examples/                    # Usage examples
│   ├── basic_usage.py
│   ├── full_ohlc_usage.py
│   ├── custom_config_usage.py
│   ├── ibkr_usage.py            # IBKR integration examples
│   ├── sample_data_with_spike.csv
│   └── sample_data_stable.csv
├── config/
│   └── default_config.yaml      # Default configuration
├── pyproject.toml               # Package configuration
├── requirements.txt             # Dependencies
├── README.md                    # This file
└── LICENSE                      # GPL-3.0 license
```

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage report
pytest --cov=market_state_detector --cov-report=html

# Run specific test file
pytest tests/test_detector.py
```

## How It Works

The detector uses three independent signals to identify high-uncertainty market regimes:

1. **Volatility Spikes**: Compares the most recent day's absolute return to historical volatility (standard deviation of returns over lookback period). Flags if recent return exceeds threshold × historical volatility.

2. **Price Gaps**: Compares opening price to previous close. Flags if gap exceeds threshold percentage, indicating potential overnight news or market stress.

3. **Wide Ranges**: Compares today's high-low range (as % of close) to average range over lookback period. Flags if current range exceeds average × (1 + threshold%).

**Stage 1 Detection**: If ANY signal triggers, the system flags a potential high-uncertainty regime. This conservative approach helps avoid false negatives during genuinely uncertain conditions.

## Design Philosophy

- **Simple and Transparent**: Uses basic, well-understood metrics
- **Not Predictive**: Only describes current observable behavior
- **Automation Over Prediction**: Reduces human error in manual checks
- **Config-Driven**: Easy to adjust for different markets/timeframes
- **No Data Included**: Users must provide their own market data
- **Modular**: Each component can be used independently

## Important Disclaimers

⚠️ **This tool is for informational purposes only**

- NOT financial advice
- NOT a trading system
- NOT predictive of future prices
- Does NOT guarantee accuracy
- User assumes all risk

This tool automates simple observations about price behavior. It cannot predict market direction or guarantee that flagged conditions represent actual risk.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This tool implements basic technical analysis concepts that are well-established in financial markets literature. It automates manual checks rather than introducing novel prediction methods.
