"""
market-state-detector: A tool to detect high-uncertainty market regimes.

This package provides functionality to detect Stage 1 (high-uncertainty) market
conditions using simple daily price behavior metrics such as volatility spikes,
price gaps, and trading ranges.

This is NOT a trading bot, NOT day trading, and NOT predictive. It automates
manual checks to improve consistency and reduce human error in identifying
uncertain market conditions.
"""

__version__ = "0.1.0"
__author__ = "market-state-detector contributors"
__license__ = "GPL-3.0"

from .detector import MarketStateDetector
from .config import Config

__all__ = ["MarketStateDetector", "Config"]
