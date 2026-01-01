"""
Tests for IBKR data fetching module.

Note: These tests focus on structure and error handling.
They do NOT test actual IBKR connections (which require running TWS/Gateway).
"""

import pytest

from market_state_detector.ibkr_data import IBKRDataFetcher


def test_fetcher_initialization():
    """Test that fetcher can be initialized with default and custom parameters."""
    # Default initialization
    fetcher = IBKRDataFetcher()
    assert fetcher.host == '127.0.0.1'
    assert fetcher.port == 7497
    assert fetcher.client_id == 1
    assert not fetcher.is_connected()

    # Custom initialization
    fetcher_custom = IBKRDataFetcher(host='192.168.1.100', port=4002, client_id=5)
    assert fetcher_custom.host == '192.168.1.100'
    assert fetcher_custom.port == 4002
    assert fetcher_custom.client_id == 5


def test_connect_without_ibinsync():
    """Test that appropriate error is raised when ib_insync is not available."""
    # This test will pass if ib_insync IS installed, skip if that's the case
    try:
        import ib_insync
        pytest.skip("ib_insync is installed, skipping import error test")
    except ImportError:
        pass

    fetcher = IBKRDataFetcher()

    with pytest.raises(ImportError) as excinfo:
        fetcher.connect()

    assert "ib_insync" in str(excinfo.value).lower()


def test_fetch_without_connection():
    """Test that fetching without connection raises appropriate error."""
    fetcher = IBKRDataFetcher()

    with pytest.raises(ConnectionError) as excinfo:
        fetcher.fetch_daily_bars('AAPL', days=30)

    assert "not connected" in str(excinfo.value).lower()


def test_disconnect_when_not_connected():
    """Test that disconnect is safe to call when not connected."""
    fetcher = IBKRDataFetcher()
    # Should not raise any error
    fetcher.disconnect()
    assert not fetcher.is_connected()


def test_context_manager_interface():
    """Test that fetcher has context manager methods."""
    fetcher = IBKRDataFetcher()

    # Check that context manager methods exist
    assert hasattr(fetcher, '__enter__')
    assert hasattr(fetcher, '__exit__')
    assert callable(fetcher.__enter__)
    assert callable(fetcher.__exit__)


# Note: The following tests would require actual IBKR connection
# and are excluded from standard test suite

# @pytest.mark.integration
# @pytest.mark.skip(reason="Requires TWS/Gateway running")
# def test_actual_connection():
#     """Integration test for actual IBKR connection."""
#     fetcher = IBKRDataFetcher(port=7497)
#     try:
#         fetcher.connect()
#         assert fetcher.is_connected()
#     finally:
#         fetcher.disconnect()


# @pytest.mark.integration
# @pytest.mark.skip(reason="Requires TWS/Gateway running")
# def test_fetch_real_data():
#     """Integration test for fetching real data."""
#     with IBKRDataFetcher(port=7497) as fetcher:
#         data = fetcher.fetch_daily_bars('AAPL', days=10)
#
#         assert 'opens' in data
#         assert 'highs' in data
#         assert 'lows' in data
#         assert 'closes' in data
#
#         assert len(data['opens']) > 0
#         assert len(data['opens']) == len(data['closes'])
