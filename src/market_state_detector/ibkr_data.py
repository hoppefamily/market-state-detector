"""
Optional IBKR/CapTrader data ingestion module.

This module provides functionality to fetch daily OHLC data from Interactive Brokers
or CapTrader using the ib_insync library. This is an OPTIONAL component - the
market-state-detector core functionality works with any data source.

Note: Requires ib_insync to be installed separately:
    pip install ib_insync

Also requires TWS (Trader Workstation) or IB Gateway to be running and configured
to accept API connections.
"""

import asyncio
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Fix for Python 3.10+ event loop requirement
# ib_insync needs an event loop to be available during import
if sys.version_info >= (3, 10):
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        # Create a new event loop if none exists
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)


class IBKRDataFetcher:
    """
    Fetch daily OHLC data from Interactive Brokers / CapTrader.

    This class provides a simple interface to retrieve historical daily bar data
    from IBKR that can be directly used with MarketStateDetector.

    Requirements:
        - ib_insync library installed
        - TWS or IB Gateway running
        - API connections enabled in TWS/Gateway settings

    Example:
        >>> fetcher = IBKRDataFetcher(host='127.0.0.1', port=7497, client_id=1)
        >>> fetcher.connect()
        >>> data = fetcher.fetch_daily_bars('AAPL', days=30)
        >>> fetcher.disconnect()
        >>>
        >>> # Use with detector
        >>> detector = MarketStateDetector()
        >>> results = detector.analyze(**data)
    """

    def __init__(self, host: str = '127.0.0.1', port: int = 7497, client_id: int = 1):
        """
        Initialize IBKR data fetcher.

        Args:
            host: Host address of TWS/Gateway (default: localhost)
            port: Port number for API connection
                  7497 for TWS paper trading
                  7496 for TWS live trading
                  4002 for IB Gateway paper trading
                  4001 for IB Gateway live trading
            client_id: Unique client identifier (1-32)
        """
        self.host = host
        self.port = port
        self.client_id = client_id
        self.ib = None
        self._connected = False

    def connect(self, timeout: int = 10) -> bool:
        """
        Connect to TWS or IB Gateway.

        Args:
            timeout: Connection timeout in seconds

        Returns:
            True if connection successful

        Raises:
            ImportError: If ib_insync is not installed
            ConnectionError: If connection fails
        """
        try:
            from ib_insync import IB
        except ImportError:
            raise ImportError(
                "ib_insync library is required for IBKR data fetching. "
                "Install with: pip install ib_insync"
            )

        self.ib = IB()

        try:
            self.ib.connect(self.host, self.port, clientId=self.client_id, timeout=timeout)
            self._connected = True
            return True
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to IBKR at {self.host}:{self.port}. "
                f"Make sure TWS/Gateway is running and API connections are enabled. "
                f"Error: {str(e)}"
            )

    def disconnect(self):
        """Disconnect from TWS/Gateway."""
        if self.ib and self._connected:
            self.ib.disconnect()
            self._connected = False

    def is_connected(self) -> bool:
        """Check if currently connected to IBKR."""
        return self._connected and self.ib is not None

    def fetch_daily_bars(
        self,
        symbol: str,
        days: int = 30,
        exchange: str = 'SMART',
        currency: str = 'USD',
        security_type: str = 'STK',
        end_date: Optional[datetime] = None
    ) -> Dict[str, List[float]]:
        """
        Fetch daily OHLC bars for a symbol.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            days: Number of daily bars to fetch (default: 30)
            exchange: Exchange routing (default: 'SMART' for automatic routing)
            currency: Currency (default: 'USD')
            security_type: Security type (default: 'STK' for stocks)
                          Other options: 'OPT', 'FUT', 'CASH', 'CFD'
            end_date: End date for historical data (default: today)

        Returns:
            Dictionary with keys: 'opens', 'highs', 'lows', 'closes'
            Each contains a list of floats ordered chronologically (oldest first)

        Raises:
            ConnectionError: If not connected to IBKR
            ValueError: If symbol not found or data unavailable
        """
        if not self.is_connected():
            raise ConnectionError(
                "Not connected to IBKR. Call connect() first."
            )

        try:
            from ib_insync import Contract, Stock
        except ImportError:
            raise ImportError("ib_insync library is required")

        # Create contract
        if security_type == 'STK':
            contract = Stock(symbol, exchange, currency)
        else:
            contract = Contract(
                symbol=symbol,
                secType=security_type,
                exchange=exchange,
                currency=currency
            )

        # Qualify the contract to ensure it's valid
        qualified_contracts = self.ib.qualifyContracts(contract)
        if not qualified_contracts:
            raise ValueError(
                f"Could not find contract for symbol '{symbol}' on {exchange}. "
                f"Check symbol and exchange are correct."
            )

        contract = qualified_contracts[0]

        # Calculate duration string
        duration = f"{days} D"

        # Set end date
        if end_date is None:
            end_date = datetime.now()

        # Format end date for IBKR API
        end_date_str = end_date.strftime("%Y%m%d %H:%M:%S")

        # Request historical data
        try:
            bars = self.ib.reqHistoricalData(
                contract,
                endDateTime=end_date_str,
                durationStr=duration,
                barSizeSetting='1 day',
                whatToShow='TRADES',
                useRTH=True,  # Regular trading hours only
                formatDate=1
            )
        except Exception as e:
            raise ValueError(
                f"Failed to fetch data for {symbol}. "
                f"Error: {str(e)}"
            )

        if not bars:
            raise ValueError(
                f"No data returned for {symbol}. "
                f"Check that the symbol has trading data for the requested period."
            )

        # Extract OHLC data
        opens = [float(bar.open) for bar in bars]
        highs = [float(bar.high) for bar in bars]
        lows = [float(bar.low) for bar in bars]
        closes = [float(bar.close) for bar in bars]

        return {
            'opens': opens,
            'highs': highs,
            'lows': lows,
            'closes': closes
        }

    def fetch_multiple_symbols(
        self,
        symbols: List[str],
        days: int = 30,
        exchange: str = 'SMART',
        currency: str = 'USD'
    ) -> Dict[str, Dict[str, List[float]]]:
        """
        Fetch daily bars for multiple symbols.

        Args:
            symbols: List of ticker symbols
            days: Number of daily bars to fetch for each symbol
            exchange: Exchange routing
            currency: Currency

        Returns:
            Dictionary mapping symbol -> OHLC data dict

        Example:
            >>> data = fetcher.fetch_multiple_symbols(['AAPL', 'MSFT', 'GOOGL'])
            >>> aapl_data = data['AAPL']
            >>> detector.analyze(**aapl_data)
        """
        results = {}

        for symbol in symbols:
            try:
                results[symbol] = self.fetch_daily_bars(
                    symbol=symbol,
                    days=days,
                    exchange=exchange,
                    currency=currency
                )
            except Exception as e:
                print(f"Warning: Failed to fetch data for {symbol}: {str(e)}")
                results[symbol] = None

        return results

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


def fetch_ibkr_data(
    symbol: str,
    days: int = 30,
    host: str = '127.0.0.1',
    port: int = 7497,
    client_id: int = 1,
    **kwargs
) -> Dict[str, List[float]]:
    """
    Convenience function to fetch IBKR data with automatic connection handling.

    This is a simpler interface for one-off data fetches. For multiple fetches,
    consider using IBKRDataFetcher directly with a persistent connection.

    Args:
        symbol: Stock ticker symbol
        days: Number of daily bars to fetch
        host: TWS/Gateway host address
        port: TWS/Gateway port number
        client_id: Client identifier
        **kwargs: Additional arguments passed to fetch_daily_bars()

    Returns:
        Dictionary with OHLC data ready for MarketStateDetector

    Example:
        >>> from market_state_detector import MarketStateDetector
        >>> from market_state_detector.ibkr_data import fetch_ibkr_data
        >>>
        >>> # Fetch data from IBKR
        >>> data = fetch_ibkr_data('AAPL', days=30, port=7497)
        >>>
        >>> # Analyze with detector
        >>> detector = MarketStateDetector()
        >>> results = detector.analyze(**data)
    """
    with IBKRDataFetcher(host=host, port=port, client_id=client_id) as fetcher:
        return fetcher.fetch_daily_bars(symbol, days=days, **kwargs)
