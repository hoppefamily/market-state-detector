"""
Optional Alpaca data ingestion module.

This module provides functionality to fetch daily OHLC data from Alpaca Markets
using the alpaca-py library. This is an OPTIONAL component - the
market-state-detector core functionality works with any data source.

Note: Requires alpaca-py to be installed separately:
    pip install alpaca-py

Alpaca provides commission-free trading and market data for US equities.
Sign up at https://alpaca.markets/ for API keys.

Important: Alpaca only supports US equities. Forex, futures, and international
stocks are not available.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class AlpacaDataFetcher:
    """
    Fetch daily OHLC data from Alpaca Markets.

    This class provides a simple interface to retrieve historical daily bar data
    from Alpaca that can be directly used with MarketStateDetector.

    Requirements:
        - alpaca-py library installed
        - Alpaca API key and secret key (get free account at alpaca.markets)

    Example:
        >>> fetcher = AlpacaDataFetcher(api_key='YOUR_KEY', secret_key='YOUR_SECRET')
        >>> data = fetcher.fetch_daily_bars('AAPL', days=30)
        >>>
        >>> # Use with detector
        >>> from market_state_detector import MarketStateDetector
        >>> detector = MarketStateDetector()
        >>> results = detector.analyze(**data)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        paper: bool = True
    ):
        """
        Initialize Alpaca data fetcher.

        Args:
            api_key: Alpaca API key (or set ALPACA_API_KEY environment variable)
            secret_key: Alpaca secret key (or set ALPACA_SECRET_KEY environment variable)
            paper: Paper trading indicator (default: True). Note: This parameter
                   is kept for API consistency but does not affect data fetching.
                   Historical data access uses the same endpoint for both paper
                   and live keys. The paper/live distinction matters only for
                   trading operations.

        Note:
            Paper trading is recommended for testing and development.
            API keys from paper and live accounts are different.
        """
        # Get API keys from parameters or environment variables
        self.api_key = api_key or os.getenv('ALPACA_API_KEY')
        self.secret_key = secret_key or os.getenv('ALPACA_SECRET_KEY')

        if not self.api_key or not self.secret_key:
            raise ValueError(
                "API key and secret key are required. "
                "Provide them as parameters or set ALPACA_API_KEY and "
                "ALPACA_SECRET_KEY environment variables."
            )

        self.paper = paper
        self.client = None

    def _validate_symbol(self, symbol: str) -> None:
        """
        Validate that symbol is a US equity (not forex/futures).

        Args:
            symbol: Ticker symbol to validate

        Raises:
            ValueError: If symbol appears to be forex, futures, or other non-equity
        """
        symbol_upper = symbol.upper()

        # Check for forex patterns
        if '/' in symbol_upper:
            raise ValueError(
                f"Symbol '{symbol}' appears to be a forex pair. "
                f"Alpaca only supports US equities. "
                f"Try stock symbols like 'AAPL', 'MSFT', 'TSLA'."
            )

        # Check for common forex currency codes (6 chars like EURUSD)
        if len(symbol_upper) == 6 and symbol_upper.isalpha():
            common_currencies = ['EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD', 'USD']
            # Check if both first 3 and last 3 chars are currency codes
            first_three = symbol_upper[:3]
            last_three = symbol_upper[3:]
            if first_three in common_currencies and last_three in common_currencies:
                raise ValueError(
                    f"Symbol '{symbol}' appears to be a forex pair. "
                    f"Alpaca only supports US equities."
                )

        # Check for futures indicators - common futures symbols
        # Matches patterns like ESH23, CLZ24, GCF25 (root + month + year)
        common_futures_roots = ['ES', 'CL', 'GC', 'NQ', 'YM', 'RTY', 'ZN', 'ZB', 'ZC', 'ZS', 'NG']

        # Reject bare futures root symbols (e.g., 'ES', 'CL')
        if symbol_upper in common_futures_roots:
            raise ValueError(
                f"Symbol '{symbol}' appears to be a futures contract. "
                f"Alpaca only supports US equities."
            )

        if len(symbol_upper) >= 4:
            # Check for known futures roots followed by month code and year
            for root in common_futures_roots:
                if symbol_upper.startswith(root) and len(symbol_upper) == len(root) + 3:
                    # Check if follows pattern: ROOT + letter (month) + 2 digits (year)
                    remainder = symbol_upper[len(root):]
                    if len(remainder) == 3 and remainder[0].isalpha() and remainder[1:].isdigit():
                        raise ValueError(
                            f"Symbol '{symbol}' appears to be a futures contract. "
                            f"Alpaca only supports US equities."
                        )

        # Check for "FUT" in symbol name
        if 'FUT' in symbol_upper:
            raise ValueError(
                f"Symbol '{symbol}' appears to be a futures contract. "
                f"Alpaca only supports US equities."
            )

    def _get_client(self):
        """
        Lazy initialization of Alpaca client.

        Returns:
            StockHistoricalDataClient instance
        """
        if self.client is None:
            try:
                from alpaca.data.historical import StockHistoricalDataClient
            except ImportError:
                raise ImportError(
                    "alpaca-py library is required for Alpaca data fetching. "
                    "Install with: pip install alpaca-py"
                )

            # Note: StockHistoricalDataClient uses the same data endpoint
            # for both paper and live keys. The paper/live distinction only
            # matters for trading operations, not historical data fetching.
            self.client = StockHistoricalDataClient(
                api_key=self.api_key,
                secret_key=self.secret_key
            )

        return self.client

    def fetch_daily_bars(
        self,
        symbol: str,
        days: int = 25,
        end_date: Optional[datetime] = None
    ) -> Dict[str, List[float]]:
        """
        Fetch daily OHLC bars for a symbol.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
                Note: Only US equities are supported
            days: Number of daily bars to fetch (default: 25, matches Alpaca free tier)
            end_date: End date for historical data (default: today)

        Returns:
            Dictionary with keys: 'opens', 'highs', 'lows', 'closes'
            Each contains a list of floats ordered chronologically (oldest first)

        Raises:
            ValueError: If symbol is not a US equity or data unavailable
            ImportError: If alpaca-py is not installed
        """
        # Validate symbol is US equity
        self._validate_symbol(symbol)

        # Get client
        client = self._get_client()

        try:
            from alpaca.data.enums import DataFeed
            from alpaca.data.requests import StockBarsRequest
            from alpaca.data.timeframe import TimeFrame
        except ImportError:
            raise ImportError("alpaca-py library is required")

        # Calculate start date
        if end_date is None:
            end_date = datetime.now()

        start_date = end_date - timedelta(days=days + 10)  # Buffer for weekends/holidays

        # Create request
        # Use IEX feed for free tier compatibility (SIP requires paid subscription)
        request = StockBarsRequest(
            symbol_or_symbols=symbol.upper(),
            timeframe=TimeFrame.Day,
            start=start_date,
            end=end_date,
            feed=DataFeed.IEX  # Use IEX feed (free tier compatible)
        )

        # Fetch data
        try:
            bars_response = client.get_stock_bars(request)
        except Exception as e:
            raise ValueError(
                f"Failed to fetch data for '{symbol}'. "
                f"Error: {str(e)}"
            )

        # Extract bars for the symbol
        # alpaca-py returns a BarSet object with symbol keys
        symbol_key = symbol.upper()

        # Try different ways to access the data based on alpaca-py version
        bars = None
        if hasattr(bars_response, 'data') and symbol_key in bars_response.data:
            bars = bars_response.data[symbol_key]
        elif symbol_key in bars_response:
            bars = bars_response[symbol_key]
        elif hasattr(bars_response, symbol_key):
            bars = getattr(bars_response, symbol_key)

        if not bars:
            raise ValueError(
                f"No data returned for '{symbol}'. "
                f"Check that the symbol is valid and has trading data. "
                f"(Response type: {type(bars_response).__name__})"
            )

        # Sort bars by timestamp (should already be sorted, but ensure it)
        bars_list = sorted(bars, key=lambda x: x.timestamp)

        # Limit to requested number of days
        bars_list = bars_list[-days:] if len(bars_list) > days else bars_list

        if len(bars_list) < days:
            logger.info(
                f"Only {len(bars_list)} bars available for '{symbol}' "
                f"(requested {days}). This is normal for Alpaca free tier."
            )

        # Extract OHLC data
        opens = [float(bar.open) for bar in bars_list]
        highs = [float(bar.high) for bar in bars_list]
        lows = [float(bar.low) for bar in bars_list]
        closes = [float(bar.close) for bar in bars_list]

        return {
            'opens': opens,
            'highs': highs,
            'lows': lows,
            'closes': closes
        }

    def fetch_multiple_symbols(
        self,
        symbols: List[str],
        days: int = 25,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Dict[str, List[float]]]:
        """
        Fetch daily bars for multiple symbols.

        Args:
            symbols: List of ticker symbols (US equities only)
            days: Number of daily bars to fetch for each symbol
            end_date: End date for historical data (default: today)

        Returns:
            Dictionary mapping symbol -> OHLC data dict
            Failed fetches will have None as value

        Example:
            >>> data = fetcher.fetch_multiple_symbols(['AAPL', 'MSFT', 'GOOGL'])
            >>> aapl_data = data['AAPL']
            >>> if aapl_data:
            >>>     detector.analyze(**aapl_data)
        """
        results = {}

        for symbol in symbols:
            try:
                results[symbol] = self.fetch_daily_bars(
                    symbol=symbol,
                    days=days,
                    end_date=end_date
                )
            except Exception as e:
                logger.warning(f"Failed to fetch data for {symbol}: {str(e)}")
                results[symbol] = None

        return results

    def __enter__(self):
        """Context manager entry."""
        # Client is initialized lazily on first use
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Alpaca client doesn't require explicit cleanup
        pass


def fetch_alpaca_data(
    symbol: str,
    days: int = 25,
    api_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    paper: bool = True,
    **kwargs
) -> Dict[str, List[float]]:
    """
    Convenience function to fetch Alpaca data with automatic connection handling.

    This is a simpler interface for one-off data fetches. For multiple fetches,
    consider using AlpacaDataFetcher directly.

    Args:
        symbol: Stock ticker symbol (US equities only)
        days: Number of daily bars to fetch
        api_key: Alpaca API key (or set ALPACA_API_KEY env var)
        secret_key: Alpaca secret key (or set ALPACA_SECRET_KEY env var)
        paper: Use paper trading endpoint (default: True)
        **kwargs: Additional arguments passed to fetch_daily_bars()

    Returns:
        Dictionary with OHLC data ready for MarketStateDetector

    Example:
        >>> from market_state_detector import MarketStateDetector
        >>> from market_state_detector.alpaca_data import fetch_alpaca_data
        >>>
        >>> # Fetch data from Alpaca
        >>> data = fetch_alpaca_data('AAPL', days=30)
        >>>
        >>> # Analyze with detector
        >>> detector = MarketStateDetector()
        >>> results = detector.analyze(**data)
    """
    with AlpacaDataFetcher(api_key=api_key, secret_key=secret_key, paper=paper) as fetcher:
        return fetcher.fetch_daily_bars(symbol, days=days, **kwargs)
