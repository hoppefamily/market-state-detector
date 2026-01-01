"""
Main market state detector module.

This module integrates volatility, gap, and range analysis to detect
high-uncertainty market regimes (Stage 1 conditions).
"""

from typing import Dict, List, Optional
from .config import Config
from .volatility import detect_volatility_spike
from .gaps import detect_gap_from_prices
from .ranges import detect_wide_range


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
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the market state detector.
        
        Args:
            config: Configuration object. If None, uses default configuration.
        """
        self.config = config or Config()
    
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
