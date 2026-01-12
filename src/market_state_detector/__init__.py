"""
market-state-detector: A tool to detect high-uncertainty market regimes.

This package provides functionality to detect Stage 1 (high-uncertainty) market
conditions using simple daily price behavior metrics such as volatility spikes,
price gaps, and trading ranges.

This is NOT a trading bot, NOT day trading, and NOT predictive. It automates
manual checks to improve consistency and reduce human error in identifying
uncertain market conditions.
"""

__version__ = "0.1.1"
__author__ = "market-state-detector contributors"
__license__ = "Apache-2.0 OR GPL-3.0-or-later"

from .config import Config
from .detector import MarketStateDetector

# Build __all__ list starting with core components
__all__ = ["MarketStateDetector", "Config"]

# Optional IBKR data fetching (requires ib_insync to be installed)
try:
    from .ibkr_data import IBKRDataFetcher, fetch_ibkr_data
    __all__.extend(["IBKRDataFetcher", "fetch_ibkr_data"])
except ImportError:
    # ib_insync not installed, IBKR functionality not available
    pass

# Optional Alpaca data fetching (requires alpaca-py to be installed)
try:
    from .alpaca_data import AlpacaDataFetcher, fetch_alpaca_data
    __all__.extend(["AlpacaDataFetcher", "fetch_alpaca_data"])
except ImportError:
    # alpaca-py not installed, Alpaca functionality not available
    pass
