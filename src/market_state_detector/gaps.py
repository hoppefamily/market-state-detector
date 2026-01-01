"""
Price gap detection module.

This module provides functionality to detect significant overnight gaps in
market prices that may indicate increased uncertainty or market stress.
"""

from typing import Tuple


def detect_gap(
    previous_close: float,
    current_open: float,
    threshold_percent: float = 2.0
) -> Tuple[bool, dict]:
    """
    Detect significant price gap between close and next open.
    
    A gap occurs when the opening price is significantly different from the
    previous day's closing price, indicating potential market discontinuity.
    
    Args:
        previous_close: Previous trading day's closing price
        current_open: Current trading day's opening price
        threshold_percent: Minimum gap size as percentage to flag
        
    Returns:
        Tuple of (gap_detected: bool, details: dict)
        Details dict contains:
            - gap_percent: Gap size as percentage
            - gap_direction: 'up' for gap up, 'down' for gap down
            - absolute_gap: Absolute price difference
            
    Raises:
        ValueError: If prices are invalid (zero or negative)
    """
    if previous_close <= 0 or current_open <= 0:
        raise ValueError("Prices must be positive")
    
    gap_absolute = current_open - previous_close
    gap_percent = (gap_absolute / previous_close) * 100
    
    gap_detected = abs(gap_percent) >= threshold_percent
    gap_direction = "up" if gap_percent > 0 else "down"
    
    details = {
        "gap_percent": gap_percent,
        "gap_direction": gap_direction,
        "absolute_gap": gap_absolute,
    }
    
    return gap_detected, details


def detect_gap_from_prices(
    closes: list,
    opens: list,
    threshold_percent: float = 2.0
) -> Tuple[bool, dict]:
    """
    Detect gap using the most recent close and open prices from lists.
    
    Args:
        closes: List of closing prices (most recent last)
        opens: List of opening prices (most recent last)
        threshold_percent: Minimum gap size as percentage to flag
        
    Returns:
        Tuple of (gap_detected: bool, details: dict)
        
    Raises:
        ValueError: If lists are too short or mismatched
    """
    if len(closes) < 2 or len(opens) < 1:
        raise ValueError("Need at least 2 closes and 1 open for gap detection")
    
    if len(opens) != len(closes):
        raise ValueError("Opens and closes lists must have same length")
    
    # Previous day's close vs current day's open
    previous_close = closes[-2]
    current_open = opens[-1]
    
    return detect_gap(previous_close, current_open, threshold_percent)
