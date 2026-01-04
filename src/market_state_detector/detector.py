"""
Main market state detector module.

This module integrates volatility, gap, and range analysis to detect
high-uncertainty market regimes (Stage 1 conditions).
"""

import logging
from typing import Dict, List, Optional

from .config import Config
from .gaps import detect_gap_from_prices
from .market_context import MarketContextAnalyzer, format_context_message
from .ranges import detect_wide_range
from .volatility import detect_volatility_spike

logger = logging.getLogger(__name__)


class MarketStateDetector:
    """
    Detect high-uncertainty market regimes using price behavior analysis.

    This class combines multiple simple metrics (volatility spikes, price gaps,
    and wide trading ranges) to identify potential Stage 1 (high-uncertainty)
    market conditions. It automates manual checks that traders might perform
    to avoid making decisions during unstable market conditions.

    This is NOT a trading bot, NOT day trading, and NOT predictive. It simply
    flags when observable price behavior suggests increased uncertainty.

    Attributes:
        config: Configuration object containing detection parameters
    """

    def __init__(self, config: Optional[Config] = None, symbol: Optional[str] = None):
        """
        Initialize the market state detector.

        Args:
            config: Configuration object. If None, uses default configuration.
            symbol: Stock symbol for stock-specific config (optional)
        """
        if config is not None:
            self.config = config
        else:
            self.config = Config(symbol=symbol)

    def analyze(
        self,
        closes: List[float],
        highs: Optional[List[float]] = None,
        lows: Optional[List[float]] = None,
        opens: Optional[List[float]] = None
    ) -> Dict:
        """
        Analyze market data to detect high-uncertainty regime.

        Args:
            closes: List of daily closing prices (most recent last)
            highs: Optional list of daily high prices (most recent last)
            lows: Optional list of daily low prices (most recent last)
            opens: Optional list of daily opening prices (most recent last)

        Returns:
            Dictionary containing:
                - stage_1_detected: Boolean indicating if Stage 1 detected
                - signals: Dict of individual signal results
                - summary: Human-readable summary

        Raises:
            ValueError: If insufficient data provided
        """
        min_points = self.config.get("general", "min_data_points")
        if len(closes) < min_points:
            raise ValueError(
                f"Need at least {min_points} closing prices for analysis"
            )

        signals = {}
        flags = []

        # Check volatility spike
        try:
            vol_config = self.config.get_section("volatility")
            spike_detected, spike_details = detect_volatility_spike(
                closes,
                threshold_multiplier=vol_config["threshold_multiplier"],
                lookback_period=vol_config["lookback_period"]
            )
            signals["volatility_spike"] = {
                "detected": spike_detected,
                "details": spike_details
            }
            if spike_detected:
                flags.append("volatility_spike")
        except Exception as e:
            signals["volatility_spike"] = {
                "detected": False,
                "error": str(e)
            }

        # Check price gap (if open prices provided)
        if opens is not None and len(opens) == len(closes):
            try:
                gap_config = self.config.get_section("gaps")
                gap_detected, gap_details = detect_gap_from_prices(
                    closes,
                    opens,
                    threshold_percent=gap_config["threshold_percent"]
                )
                signals["price_gap"] = {
                    "detected": gap_detected,
                    "details": gap_details
                }
                if gap_detected:
                    flags.append("price_gap")
            except Exception as e:
                signals["price_gap"] = {
                    "detected": False,
                    "error": str(e)
                }

        # Check wide range (if high/low prices provided)
        if highs is not None and lows is not None:
            if len(highs) == len(closes) and len(lows) == len(closes):
                try:
                    range_config = self.config.get_section("ranges")
                    wide_detected, wide_details = detect_wide_range(
                        highs,
                        lows,
                        closes,
                        threshold_percent=range_config["threshold_percent"],
                        lookback_period=range_config["lookback_period"]
                    )
                    signals["wide_range"] = {
                        "detected": wide_detected,
                        "details": wide_details
                    }
                    if wide_detected:
                        flags.append("wide_range")
                except Exception as e:
                    signals["wide_range"] = {
                        "detected": False,
                        "error": str(e)
                    }

        # Determine overall Stage 1 detection
        # Stage 1 is flagged if ANY signal is triggered
        stage_1_detected = len(flags) > 0

        # Generate summary
        if stage_1_detected:
            summary = (
                f"⚠️  HIGH UNCERTAINTY DETECTED - Stage 1 regime likely. "
                f"Signals: {', '.join(flags)}. "
                f"Consider avoiding new positions until conditions stabilize."
            )
        else:
            summary = (
                "✓ No Stage 1 signals detected. "
                "Market behavior appears within normal parameters."
            )

        return {
            "stage_1_detected": stage_1_detected,
            "signals": signals,
            "flags": flags,
            "summary": summary
        }

    def analyze_simple(self, closes: List[float]) -> bool:
        """
        Simple analysis using only closing prices.

        Args:
            closes: List of daily closing prices

        Returns:
            True if Stage 1 detected, False otherwise
        """
        result = self.analyze(closes)
        return result["stage_1_detected"]

    def analyze_with_context(
        self,
        symbol: str,
        closes: List[float],
        highs: Optional[List[float]] = None,
        lows: Optional[List[float]] = None,
        opens: Optional[List[float]] = None,
        fetcher=None,
        include_context: bool = True
    ) -> dict:
        """
        Analyze stock with market context detection.

        This method performs standard Stage 1 detection and additionally
        analyzes whether the detected volatility is market-wide, sector-specific,
        or stock-specific by comparing against major benchmarks (SPY, QQQ, DIA).

        Args:
            symbol: Stock symbol being analyzed
            closes: List of daily closing prices
            highs: Optional list of daily high prices
            lows: Optional list of daily low prices
            opens: Optional list of daily open prices
            fetcher: Optional data fetcher for benchmarks (e.g., AlpacaDataFetcher or IBKRDataFetcher)
            include_context: Whether to include market context analysis (default: True).
                Note: Market context is only analyzed when Stage 1 signals are detected in the stock.

        Returns:
            Dict with analysis results and market context information:
            - All fields from standard analyze() method
            - market_context: Dict with context analysis or None if unavailable/not requested/no Stage 1 detected
                - type: 'broad_market', 'sector', 'stock_specific', or 'normal'
                - benchmarks_affected: List of affected benchmark symbols
                - correlation_score: Float between 0 and 1
                - description: Human-readable description
                - message: Formatted message for display

        Example:
            >>> from market_state_detector import MarketStateDetector
            >>> from market_state_detector.alpaca_data import AlpacaDataFetcher
            >>>
            >>> # Fetch data for stock and analyze with context
            >>> fetcher = AlpacaDataFetcher(api_key='...', secret_key='...')
            >>> data = fetcher.fetch_daily_bars('AAPL', days=30)
            >>>
            >>> detector = MarketStateDetector()
            >>> result = detector.analyze_with_context(
            ...     symbol='AAPL',
            ...     fetcher=fetcher,
            ...     **data
            ... )
            >>>
            >>> if result['stage_1_detected']:
            ...     print(result['summary'])
            ...     if result.get('market_context'):
            ...         print(result['market_context']['message'])
        """
        # Run standard analysis
        result = self.analyze(closes, highs, lows, opens)

        # Return early if context not requested or not possible
        if not include_context or not fetcher or not result['stage_1_detected']:
            result['market_context'] = None
            return result

        # Analyze market context
        try:
            analyzer = MarketContextAnalyzer()

            # Fetch benchmark data
            benchmark_data = analyzer.get_benchmark_data(fetcher, days=len(closes))

            # Analyze each benchmark for Stage 1 signals
            benchmark_signals = {}
            for bench_symbol, bench_data in benchmark_data.items():
                if bench_data is None:
                    benchmark_signals[bench_symbol] = []
                    continue

                try:
                    bench_result = self.analyze(**bench_data)
                    benchmark_signals[bench_symbol] = bench_result.get('flags', [])
                except Exception as e:
                    logger.warning(f"Failed to analyze {bench_symbol}: {e}")
                    benchmark_signals[bench_symbol] = []

            # Get market context
            context = analyzer.analyze_context(
                symbol=symbol,
                stock_signals=result.get('flags', []),
                benchmark_signals=benchmark_signals
            )

            result['market_context'] = {
                'type': context.context_type,
                'benchmarks_affected': context.benchmarks_affected,
                'correlation_score': context.correlation_score,
                'description': context.description,
                'message': format_context_message(context)
            }

        except Exception as e:
            logger.warning(f"Failed to analyze market context: {e}")
            result['market_context'] = None

        return result
