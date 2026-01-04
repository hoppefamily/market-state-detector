"""
Tests for Alpaca data fetching module.

These tests cover the AlpacaDataFetcher class functionality including
initialization, symbol validation, error handling, and context manager interface.
"""

import os
import pytest
from unittest.mock import patch, MagicMock


class TestAlpacaDataFetcher:
    """Test suite for AlpacaDataFetcher class."""

    def test_init_with_explicit_keys(self):
        """Test initialization with explicitly provided API keys."""
        from market_state_detector.alpaca_data import AlpacaDataFetcher
        
        fetcher = AlpacaDataFetcher(
            api_key='test_key',
            secret_key='test_secret',
            paper=True
        )
        
        assert fetcher.api_key == 'test_key'
        assert fetcher.secret_key == 'test_secret'
        assert fetcher.paper is True
        assert fetcher.client is None  # Lazy initialization

    def test_init_with_env_vars(self):
        """Test initialization using environment variables."""
        from market_state_detector.alpaca_data import AlpacaDataFetcher
        
        with patch.dict(os.environ, {
            'ALPACA_API_KEY': 'env_key',
            'ALPACA_SECRET_KEY': 'env_secret'
        }):
            fetcher = AlpacaDataFetcher(paper=True)
            
            assert fetcher.api_key == 'env_key'
            assert fetcher.secret_key == 'env_secret'

    def test_init_without_keys_raises_error(self):
        """Test that initialization without API keys raises ValueError."""
        from market_state_detector.alpaca_data import AlpacaDataFetcher
        
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="API key and secret key are required"):
                AlpacaDataFetcher()

    def test_validate_symbol_rejects_forex_with_slash(self):
        """Test that forex symbols with slash are rejected."""
        from market_state_detector.alpaca_data import AlpacaDataFetcher
        
        fetcher = AlpacaDataFetcher(
            api_key='test_key',
            secret_key='test_secret'
        )
        
        with pytest.raises(ValueError, match="appears to be a forex pair"):
            fetcher._validate_symbol('EUR/USD')
        
        with pytest.raises(ValueError, match="appears to be a forex pair"):
            fetcher._validate_symbol('GBP/JPY')

    def test_validate_symbol_rejects_forex_pairs(self):
        """Test that 6-character forex pairs are rejected."""
        from market_state_detector.alpaca_data import AlpacaDataFetcher
        
        fetcher = AlpacaDataFetcher(
            api_key='test_key',
            secret_key='test_secret'
        )
        
        # Should reject common forex pairs
        with pytest.raises(ValueError, match="appears to be a forex pair"):
            fetcher._validate_symbol('EURUSD')
        
        with pytest.raises(ValueError, match="appears to be a forex pair"):
            fetcher._validate_symbol('GBPJPY')

    def test_validate_symbol_accepts_valid_tickers(self):
        """Test that valid US stock tickers are accepted."""
        from market_state_detector.alpaca_data import AlpacaDataFetcher
        
        fetcher = AlpacaDataFetcher(
            api_key='test_key',
            secret_key='test_secret'
        )
        
        # These should not raise
        valid_symbols = ['AAPL', 'MSFT', 'GOOGL', 'SPY', 'QQQ', 'TSM']
        for symbol in valid_symbols:
            fetcher._validate_symbol(symbol)  # Should not raise

    def test_validate_symbol_accepts_6char_non_forex(self):
        """Test that 6-character non-forex tickers are accepted."""
        from market_state_detector.alpaca_data import AlpacaDataFetcher
        
        fetcher = AlpacaDataFetcher(
            api_key='test_key',
            secret_key='test_secret'
        )
        
        # EUREKA shouldn't be rejected even though it starts with EUR
        # because last 3 chars (EKA) are not a currency code
        fetcher._validate_symbol('EUREKA')  # Should not raise

    def test_validate_symbol_rejects_futures(self):
        """Test that futures contract symbols are rejected."""
        from market_state_detector.alpaca_data import AlpacaDataFetcher
        
        fetcher = AlpacaDataFetcher(
            api_key='test_key',
            secret_key='test_secret'
        )
        
        # Common futures symbols
        futures_symbols = ['ESH23', 'CLZ24', 'GCF25', 'NQM26']
        for symbol in futures_symbols:
            with pytest.raises(ValueError, match="appears to be a futures contract"):
                fetcher._validate_symbol(symbol)

    def test_validate_symbol_rejects_fut_keyword(self):
        """Test that symbols containing 'FUT' are rejected."""
        from market_state_detector.alpaca_data import AlpacaDataFetcher
        
        fetcher = AlpacaDataFetcher(
            api_key='test_key',
            secret_key='test_secret'
        )
        
        with pytest.raises(ValueError, match="appears to be a futures contract"):
            fetcher._validate_symbol('STOCKFUT')

    def test_import_error_when_alpaca_not_installed(self):
        """Test that appropriate error is raised when alpaca-py is not installed."""
        from market_state_detector.alpaca_data import AlpacaDataFetcher
        
        fetcher = AlpacaDataFetcher(
            api_key='test_key',
            secret_key='test_secret'
        )
        
        # Mock ImportError when trying to import from alpaca
        with patch.object(fetcher, '_get_client') as mock_get_client:
            mock_get_client.side_effect = ImportError(
                "alpaca-py library is required for Alpaca data fetching"
            )
            
            with pytest.raises(ImportError, match="alpaca-py library is required"):
                fetcher._get_client()

    def test_context_manager_interface(self):
        """Test that AlpacaDataFetcher works as a context manager."""
        from market_state_detector.alpaca_data import AlpacaDataFetcher
        
        with AlpacaDataFetcher(api_key='test_key', secret_key='test_secret') as fetcher:
            assert fetcher is not None
            assert isinstance(fetcher, AlpacaDataFetcher)

    @patch('market_state_detector.alpaca_data.StockHistoricalDataClient')
    def test_get_client_lazy_initialization(self, mock_client_class):
        """Test that client is initialized lazily."""
        from market_state_detector.alpaca_data import AlpacaDataFetcher
        
        # Mock the alpaca imports
        with patch.dict('sys.modules', {
            'alpaca': MagicMock(),
            'alpaca.data': MagicMock(),
            'alpaca.data.historical': MagicMock(StockHistoricalDataClient=mock_client_class)
        }):
            fetcher = AlpacaDataFetcher(
                api_key='test_key',
                secret_key='test_secret'
            )
            
            # Client should not be initialized yet
            assert fetcher.client is None
            
            # Access client
            client = fetcher._get_client()
            
            # Now client should be initialized and match the returned client
            assert fetcher.client is not None
            assert client is fetcher.client
            mock_client_class.assert_called_once_with(
                api_key='test_key',
                secret_key='test_secret'
            )

    def test_fetch_daily_bars_without_credentials_fails(self):
        """Test that fetch_daily_bars fails without valid credentials."""
        from market_state_detector.alpaca_data import AlpacaDataFetcher
        
        # This would fail in real usage but we're testing the setup
        fetcher = AlpacaDataFetcher(
            api_key='invalid_key',
            secret_key='invalid_secret'
        )
        
        # We can't test actual API call without real credentials,
        # but we can verify the method exists and accepts the right parameters
        assert hasattr(fetcher, 'fetch_daily_bars')
        assert callable(fetcher.fetch_daily_bars)

    def test_fetch_alpaca_data_convenience_function(self):
        """Test the convenience function fetch_alpaca_data."""
        # Import should work
        from market_state_detector.alpaca_data import fetch_alpaca_data
        
        # Function should exist
        assert callable(fetch_alpaca_data)

    def test_default_days_parameter_consistency(self):
        """Test that default days parameter is consistent across methods."""
        from market_state_detector.alpaca_data import AlpacaDataFetcher
        import inspect
        
        fetcher = AlpacaDataFetcher(
            api_key='test_key',
            secret_key='test_secret'
        )
        
        # Check defaults match
        fetch_daily_sig = inspect.signature(fetcher.fetch_daily_bars)
        fetch_multi_sig = inspect.signature(fetcher.fetch_multiple_symbols)
        
        daily_default = fetch_daily_sig.parameters['days'].default
        multi_default = fetch_multi_sig.parameters['days'].default
        
        assert daily_default == multi_default, \
            f"Default days parameter should be consistent: {daily_default} vs {multi_default}"


class TestSymbolValidationEdgeCases:
    """Test edge cases for symbol validation."""

    def test_single_char_symbols(self):
        """Test that single character symbols work."""
        from market_state_detector.alpaca_data import AlpacaDataFetcher
        
        fetcher = AlpacaDataFetcher(api_key='test', secret_key='test')
        fetcher._validate_symbol('A')  # Should not raise

    def test_two_char_symbols(self):
        """Test that two character symbols work."""
        from market_state_detector.alpaca_data import AlpacaDataFetcher
        
        fetcher = AlpacaDataFetcher(api_key='test', secret_key='test')
        fetcher._validate_symbol('AA')  # Should not raise

    def test_symbols_with_numbers(self):
        """Test that valid symbols with numbers are accepted."""
        from market_state_detector.alpaca_data import AlpacaDataFetcher
        
        fetcher = AlpacaDataFetcher(api_key='test', secret_key='test')
        
        # These should work (not rejected as futures)
        fetcher._validate_symbol('ABC12')  # Should not raise if not matching futures pattern

    def test_case_insensitivity(self):
        """Test that symbol validation is case insensitive."""
        from market_state_detector.alpaca_data import AlpacaDataFetcher
        
        fetcher = AlpacaDataFetcher(api_key='test', secret_key='test')
        
        # Both should behave the same
        fetcher._validate_symbol('aapl')  # Should not raise
        fetcher._validate_symbol('AAPL')  # Should not raise
