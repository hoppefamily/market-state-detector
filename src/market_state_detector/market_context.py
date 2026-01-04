"""
Market context detection module.

This module analyzes whether volatility is market-wide, sector-specific,
or stock-specific by comparing a stock's behavior against major market benchmarks.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MarketContext:
    """Market context information."""
    context_type: str  # 'broad_market', 'sector', 'stock_specific', 'normal'
    benchmarks_affected: List[str]
    correlation_score: float
    description: str


class MarketContextAnalyzer:
    """
    Analyze market context by comparing stock behavior to benchmarks.
    
    This helps distinguish between:
    - Broad market volatility (all benchmarks affected)
    - Sector-specific volatility (e.g., tech sector via QQQ)
    - Stock-specific volatility (only the stock affected)
    
    Benchmarks:
    - SPY: S&P 500 (broad market, 500 large-cap US stocks)
    - QQQ: Nasdaq-100 (tech-heavy, 100 largest non-financial Nasdaq stocks)
    - DIA: Dow Jones Industrial Average (30 blue-chip US stocks)
    """
    
    DEFAULT_BENCHMARKS = ['SPY', 'QQQ', 'DIA']
    
    def __init__(self, benchmarks: Optional[List[str]] = None):
        """
        Initialize market context analyzer.
        
        Args:
            benchmarks: List of benchmark symbols to compare against.
                       Defaults to ['SPY', 'QQQ', 'DIA']
        """
        self.benchmarks = benchmarks or self.DEFAULT_BENCHMARKS
    
    def analyze_context(
        self,
        symbol: str,
        stock_signals: List[str],
        benchmark_signals: Dict[str, List[str]]
    ) -> MarketContext:
        """
        Analyze whether volatility is market-wide, sector, or stock-specific.
        
        Args:
            symbol: Stock symbol being analyzed
            stock_signals: List of uncertainty signals detected for the stock
            benchmark_signals: Dict mapping benchmark symbols to their signals
        
        Returns:
            MarketContext object with analysis results
        """
        if not stock_signals:
            return MarketContext(
                context_type='normal',
                benchmarks_affected=[],
                correlation_score=0.0,
                description='No uncertainty signals detected'
            )
        
        # Check which benchmarks also show uncertainty
        affected_benchmarks = [
            bench for bench, signals in benchmark_signals.items()
            if signals  # Has any uncertainty signals
        ]
        
        # Determine context type based on which benchmarks are affected
        num_affected = len(affected_benchmarks)
        total_benchmarks = len([b for b in benchmark_signals.keys() if benchmark_signals[b] is not None])
        
        if num_affected == 0:
            context_type = 'stock_specific'
            description = f'{symbol} volatility appears stock-specific (no benchmark correlation)'
        elif num_affected >= 2:
            # Multiple benchmarks affected = broad market
            context_type = 'broad_market'
            description = f'Broad market volatility detected ({", ".join(affected_benchmarks)} affected)'
        else:
            # Only one benchmark affected = sector-specific
            bench = affected_benchmarks[0]
            if bench == 'QQQ':
                context_type = 'sector'
                description = f'Tech sector volatility detected (QQQ affected, others stable)'
            elif bench == 'DIA':
                context_type = 'sector'
                description = f'Blue-chip sector volatility (DIA affected, others stable)'
            else:
                context_type = 'sector'
                description = f'Sector-specific volatility (only {bench} affected)'
        
        correlation_score = num_affected / total_benchmarks if total_benchmarks > 0 else 0.0
        
        return MarketContext(
            context_type=context_type,
            benchmarks_affected=affected_benchmarks,
            correlation_score=correlation_score,
            description=description
        )
    
    def get_benchmark_data(self, fetcher, days: int = 25) -> Dict[str, dict]:
        """
        Fetch data for all benchmarks.
        
        Args:
            fetcher: Data fetcher instance (e.g., AlpacaDataFetcher or IBKRDataFetcher)
            days: Number of days of historical data to fetch
        
        Returns:
            Dict mapping benchmark symbols to their OHLC data
        """
        benchmark_data = {}
        
        for benchmark in self.benchmarks:
            try:
                data = fetcher.fetch_daily_bars(benchmark, days=days)
                benchmark_data[benchmark] = data
                logger.info(f"Fetched {benchmark} benchmark data ({len(data.get('close', []))} bars)")
            except Exception as e:
                logger.warning(f"Failed to fetch {benchmark} data: {e}")
                benchmark_data[benchmark] = None
        
        return benchmark_data


def format_context_message(context: MarketContext) -> str:
    """
    Format market context into a user-friendly message.
    
    Args:
        context: MarketContext object
    
    Returns:
        Formatted string message
    """
    if context.context_type == 'normal':
        return ""
    
    emoji_map = {
        'broad_market': '📊',
        'sector': '🏢',
        'stock_specific': '🎯'
    }
    
    emoji = emoji_map.get(context.context_type, '📈')
    
    message = f"\n{emoji} Market Context: {context.description}"
    
    if context.context_type == 'broad_market':
        message += "\n💡 This appears to be a market-wide event affecting multiple indices."
    elif context.context_type == 'sector':
        message += "\n💡 This appears to be sector-specific volatility."
    else:
        message += "\n💡 This appears to be isolated to this stock (higher individual risk)."
    
    return message
