"""
Volatility spike detection module.

This module provides functionality to detect abnormal volatility spikes in
market data by comparing recent volatility to historical averages.
"""

from typing import List, Tuple
import math


def calculate_daily_returns(prices: List[float]) -> List[float]:
    """
    Calculate daily percentage returns from price data.
    
    Args:
        prices: List of daily closing prices
        
    Returns:
        List of daily percentage returns
        
    Raises:
        ValueError: If prices list is empty or contains invalid values
    """
    if not prices or len(prices) < 2:
        raise ValueError("Need at least 2 prices to calculate returns")
    
    returns = []
    for i in range(1, len(prices)):
        if prices[i-1] <= 0 or prices[i] <= 0:
            raise ValueError("Prices must be positive")
        ret = (prices[i] - prices[i-1]) / prices[i-1]
        returns.append(ret)
    
    return returns


def calculate_volatility(returns: List[float]) -> float:
    """
    Calculate standard deviation (volatility) of returns.
    
    Args:
        returns: List of daily returns
        
    Returns:
        Standard deviation of returns
        
    Raises:
        ValueError: If returns list is empty
    """
    if not returns:
        raise ValueError("Returns list cannot be empty")
    
    n = len(returns)
    mean = sum(returns) / n
    variance = sum((r - mean) ** 2 for r in returns) / n
    return math.sqrt(variance)


def detect_volatility_spike(
    prices: List[float],
    threshold_multiplier: float = 2.0,
    lookback_period: int = 20
) -> Tuple[bool, dict]:
    """
    Detect if recent volatility is abnormally high.
    
    Compares the most recent day's absolute return to the historical volatility
    calculated over the lookback period.
    
    Args:
        prices: List of daily closing prices (most recent last)
        threshold_multiplier: Multiplier for historical volatility to trigger spike
        lookback_period: Number of days to use for historical volatility
        
    Returns:
        Tuple of (spike_detected: bool, details: dict)
        Details dict contains:
            - recent_return: Most recent day's return
            - historical_volatility: Volatility over lookback period
            - threshold: Calculated threshold value
            - spike_magnitude: How many times threshold was exceeded
            
    Raises:
        ValueError: If insufficient data or invalid parameters
    """
    if len(prices) < lookback_period + 1:
        raise ValueError(
            f"Need at least {lookback_period + 1} prices for analysis"
        )
    
    # Calculate all returns
    returns = calculate_daily_returns(prices)
    
    # Get historical returns (excluding most recent)
    historical_returns = returns[-(lookback_period+1):-1]
    recent_return = returns[-1]
    
    # Calculate historical volatility
    hist_vol = calculate_volatility(historical_returns)
    threshold = hist_vol * threshold_multiplier
    
    # Check for spike
    spike_detected = abs(recent_return) > threshold
    
    details = {
        "recent_return": recent_return,
        "historical_volatility": hist_vol,
        "threshold": threshold,
        "spike_magnitude": abs(recent_return) / threshold if threshold > 0 else 0,
    }
    
    return spike_detected, details
