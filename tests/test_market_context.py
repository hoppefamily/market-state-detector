"""
Tests for market context detection module.
"""

import pytest

from market_state_detector.market_context import (
    MarketContext,
    MarketContextAnalyzer,
    format_context_message,
)


class TestMarketContext:
    """Test suite for MarketContext dataclass."""

    def test_market_context_creation(self):
        """Test creating a MarketContext object."""
        context = MarketContext(
            context_type='broad_market',
            benchmarks_affected=['SPY', 'QQQ'],
            correlation_score=0.67,
            description='Test description'
        )

        assert context.context_type == 'broad_market'
        assert context.benchmarks_affected == ['SPY', 'QQQ']
        assert context.correlation_score == 0.67
        assert context.description == 'Test description'


class TestMarketContextAnalyzer:
    """Test suite for MarketContextAnalyzer class."""

    def test_init_default_benchmarks(self):
        """Test initialization with default benchmarks."""
        analyzer = MarketContextAnalyzer()
        assert analyzer.benchmarks == ['SPY', 'QQQ', 'DIA']

    def test_init_custom_benchmarks(self):
        """Test initialization with custom benchmarks."""
        analyzer = MarketContextAnalyzer(benchmarks=['SPY', 'IWM'])
        assert analyzer.benchmarks == ['SPY', 'IWM']

    def test_analyze_context_no_signals(self):
        """Test analysis when no uncertainty signals detected."""
        analyzer = MarketContextAnalyzer()

        context = analyzer.analyze_context(
            symbol='AAPL',
            stock_signals=[],
            benchmark_signals={'SPY': [], 'QQQ': [], 'DIA': []}
        )

        assert context.context_type == 'normal'
        assert context.benchmarks_affected == []
        assert context.correlation_score == 0.0
        assert 'No uncertainty' in context.description

    def test_analyze_context_stock_specific(self):
        """Test stock-specific volatility detection."""
        analyzer = MarketContextAnalyzer()

        context = analyzer.analyze_context(
            symbol='AAPL',
            stock_signals=['volatility_spike', 'wide_range'],
            benchmark_signals={'SPY': [], 'QQQ': [], 'DIA': []}
        )

        assert context.context_type == 'stock_specific'
        assert context.benchmarks_affected == []
        assert context.correlation_score == 0.0
        assert 'AAPL' in context.description
        assert 'stock-specific' in context.description

    def test_analyze_context_broad_market(self):
        """Test broad market volatility detection."""
        analyzer = MarketContextAnalyzer()

        context = analyzer.analyze_context(
            symbol='AAPL',
            stock_signals=['volatility_spike'],
            benchmark_signals={
                'SPY': ['volatility_spike'],
                'QQQ': ['wide_range'],
                'DIA': ['price_gap']
            }
        )

        assert context.context_type == 'broad_market'
        assert len(context.benchmarks_affected) == 3
        assert set(context.benchmarks_affected) == {'SPY', 'QQQ', 'DIA'}
        assert context.correlation_score == 1.0
        assert 'Broad market' in context.description

    def test_analyze_context_tech_sector(self):
        """Test tech sector-specific volatility detection."""
        analyzer = MarketContextAnalyzer()

        context = analyzer.analyze_context(
            symbol='AAPL',
            stock_signals=['volatility_spike'],
            benchmark_signals={
                'SPY': [],
                'QQQ': ['volatility_spike', 'wide_range'],
                'DIA': []
            }
        )

        assert context.context_type == 'sector'
        assert context.benchmarks_affected == ['QQQ']
        assert context.correlation_score == pytest.approx(0.33, rel=0.1)
        assert 'Tech sector' in context.description

    def test_analyze_context_other_sector(self):
        """Test non-tech sector-specific volatility detection."""
        analyzer = MarketContextAnalyzer()

        context = analyzer.analyze_context(
            symbol='BA',
            stock_signals=['price_gap'],
            benchmark_signals={
                'SPY': [],
                'QQQ': [],
                'DIA': ['price_gap']
            }
        )

        assert context.context_type == 'sector'
        assert context.benchmarks_affected == ['DIA']
        assert 'Blue-chip' in context.description or 'DIA' in context.description

    def test_analyze_context_partial_benchmarks(self):
        """Test analysis when some benchmarks have no data."""
        analyzer = MarketContextAnalyzer()

        context = analyzer.analyze_context(
            symbol='AAPL',
            stock_signals=['volatility_spike'],
            benchmark_signals={
                'SPY': ['volatility_spike'],
                'QQQ': None,  # No data
                'DIA': []
            }
        )

        # Should still work with partial data
        assert context.context_type in ['broad_market', 'sector', 'stock_specific']
        assert context.correlation_score >= 0.0


class TestFormatContextMessage:
    """Test suite for format_context_message function."""

    def test_format_normal_context(self):
        """Test formatting for normal market conditions."""
        context = MarketContext(
            context_type='normal',
            benchmarks_affected=[],
            correlation_score=0.0,
            description='No uncertainty signals'
        )

        message = format_context_message(context)
        assert message == ""

    def test_format_broad_market_context(self):
        """Test formatting for broad market volatility."""
        context = MarketContext(
            context_type='broad_market',
            benchmarks_affected=['SPY', 'QQQ', 'DIA'],
            correlation_score=1.0,
            description='Broad market volatility detected'
        )

        message = format_context_message(context)
        assert '📊' in message
        assert 'Market Context:' in message
        assert 'Broad market volatility' in message
        assert 'market-wide event' in message

    def test_format_sector_context(self):
        """Test formatting for sector-specific volatility."""
        context = MarketContext(
            context_type='sector',
            benchmarks_affected=['QQQ'],
            correlation_score=0.33,
            description='Tech sector volatility'
        )

        message = format_context_message(context)
        assert '🏢' in message
        assert 'Market Context:' in message
        assert 'sector-specific' in message

    def test_format_stock_specific_context(self):
        """Test formatting for stock-specific volatility."""
        context = MarketContext(
            context_type='stock_specific',
            benchmarks_affected=[],
            correlation_score=0.0,
            description='AAPL volatility appears stock-specific'
        )

        message = format_context_message(context)
        assert '🎯' in message
        assert 'Market Context:' in message
        assert 'isolated to this stock' in message
        assert 'higher individual risk' in message
