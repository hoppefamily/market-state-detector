"""
Trading range analysis module.

This module provides functionality to detect abnormally wide trading ranges
that may indicate increased market uncertainty or volatility.
"""

from typing import List, Tuple


def calculate_range_percent(high: float, low: float, close: float) -> float:
    """
    Calculate the trading range as percentage of close price.
    
    Args:
        high: Day's high price
        low: Day's low price
        close: Day's closing price
        
    Returns:
        Range as percentage of close
        
    Raises:
        ValueError: If prices are invalid
    """
    if high <= 0 or low <= 0 or close <= 0:
        raise ValueError("Prices must be positive")
    
    if high < low:
        raise ValueError("High must be greater than or equal to low")
    
    range_absolute = high - low
    range_percent = (range_absolute / close) * 100
    
    return range_percent


def calculate_average_range(
    highs: List[float],
    lows: List[float],
    closes: List[float],
    period: int
) -> float:
    """
    Calculate average trading range over a period.
    
    Args:
        highs: List of high prices
        lows: List of low prices
        closes: List of close prices
        period: Number of days to average over
        
    Returns:
        Average range as percentage
        
    Raises:
        ValueError: If lists are mismatched or too short
    """
    if len(highs) != len(lows) or len(highs) != len(closes):
        raise ValueError("All price lists must have same length")
    
    if len(highs) < period:
        raise ValueError(f"Need at least {period} data points")
    
    # Calculate ranges for the period
    ranges = []
    for i in range(-period, 0):
        range_pct = calculate_range_percent(highs[i], lows[i], closes[i])
        ranges.append(range_pct)
    
    return sum(ranges) / len(ranges)


def detect_wide_range(
    highs: List[float],
    lows: List[float],
    closes: List[float],
    threshold_percent: float = 50.0,
    lookback_period: int = 20
) -> Tuple[bool, dict]:
    """
    Detect if current trading range is abnormally wide.
    
    Compares today's trading range to the average range over the lookback period.
    Flags if current range exceeds average by the threshold percentage.
    
    Args:
        highs: List of daily high prices (most recent last)
        lows: List of daily low prices (most recent last)
        closes: List of daily close prices (most recent last)
        threshold_percent: Percent increase over average to trigger detection
        lookback_period: Number of days to use for average calculation
        
    Returns:
        Tuple of (wide_range_detected: bool, details: dict)
        Details dict contains:
            - current_range: Today's range as percentage
            - average_range: Historical average range
            - threshold: Calculated threshold value
            - range_expansion: How much wider than threshold
            
    Raises:
        ValueError: If insufficient data or invalid parameters
    """
    if len(highs) < lookback_period + 1:
        raise ValueError(
            f"Need at least {lookback_period + 1} data points"
        )
    
    # Calculate current range
    current_range = calculate_range_percent(highs[-1], lows[-1], closes[-1])
    
    # Calculate historical average (excluding current day)
    avg_range = calculate_average_range(
        highs[:-1], lows[:-1], closes[:-1], lookback_period
    )
    
    # Calculate threshold
    threshold = avg_range * (1 + threshold_percent / 100)
    
    # Check for wide range
    wide_range_detected = current_range > threshold
    
    details = {
        "current_range": current_range,
        "average_range": avg_range,
        "threshold": threshold,
        "range_expansion": (current_range / threshold - 1) * 100 if threshold > 0 else 0,
    }
    
    return wide_range_detected, details
