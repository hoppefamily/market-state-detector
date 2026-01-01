"""
Command-line interface for market state detector.

This module provides a CLI for analyzing market data from CSV files or
direct input to detect high-uncertainty market regimes.
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import List, Optional

from .detector import MarketStateDetector
from .config import Config


def load_csv_data(
    filepath: str,
    close_col: str = "close",
    high_col: Optional[str] = "high",
    low_col: Optional[str] = "low",
    open_col: Optional[str] = "open"
) -> dict:
    """
    Load market data from CSV file.
    
    Args:
        filepath: Path to CSV file
        close_col: Column name for closing prices
        high_col: Column name for high prices (optional)
        low_col: Column name for low prices (optional)
        open_col: Column name for opening prices (optional)
        
    Returns:
        Dictionary with price lists
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If required columns are missing
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    data = {
        "closes": [],
        "highs": [],
        "lows": [],
        "opens": []
    }
    
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            if close_col not in row:
                raise ValueError(f"Required column '{close_col}' not found in CSV")
            
            data["closes"].append(float(row[close_col]))
            
            if high_col and high_col in row:
                data["highs"].append(float(row[high_col]))
            
            if low_col and low_col in row:
                data["lows"].append(float(row[low_col]))
            
            if open_col and open_col in row:
                data["opens"].append(float(row[open_col]))
    
    # Only include optional data if we got all rows
    if len(data["highs"]) != len(data["closes"]):
        data["highs"] = None
    if len(data["lows"]) != len(data["closes"]):
        data["lows"] = None
    if len(data["opens"]) != len(data["closes"]):
        data["opens"] = None
    
    return data


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Detect high-uncertainty market regimes (Stage 1) using price behavior.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze data from CSV file
  market-state-detector --csv data.csv
  
  # Use custom config file
  market-state-detector --csv data.csv --config custom_config.yaml
  
  # Specify custom column names
  market-state-detector --csv data.csv --close-col Close --high-col High
  
  # Get JSON output for scripting
  market-state-detector --csv data.csv --json

Note: This tool automates manual checks for market uncertainty.
      It is NOT a trading bot and NOT predictive.
        """
    )
    
    parser.add_argument(
        "--csv",
        type=str,
        help="Path to CSV file containing market data"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to custom configuration YAML file"
    )
    
    parser.add_argument(
        "--close-col",
        type=str,
        default="close",
        help="Column name for closing prices (default: close)"
    )
    
    parser.add_argument(
        "--high-col",
        type=str,
        default="high",
        help="Column name for high prices (default: high)"
    )
    
    parser.add_argument(
        "--low-col",
        type=str,
        default="low",
        help="Column name for low prices (default: low)"
    )
    
    parser.add_argument(
        "--open-col",
        type=str,
        default="open",
        help="Column name for opening prices (default: open)"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="market-state-detector 0.1.0"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.csv:
        parser.print_help()
        sys.exit(1)
    
    try:
        # Load configuration
        config = Config(args.config) if args.config else Config()
        
        # Load data
        data = load_csv_data(
            args.csv,
            close_col=args.close_col,
            high_col=args.high_col,
            low_col=args.low_col,
            open_col=args.open_col
        )
        
        # Run detection
        detector = MarketStateDetector(config)
        results = detector.analyze(
            closes=data["closes"],
            highs=data["highs"],
            lows=data["lows"],
            opens=data["opens"]
        )
        
        # Output results
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print("\n" + "="*70)
            print("MARKET STATE DETECTION RESULTS")
            print("="*70)
            print(f"\n{results['summary']}\n")
            
            if results['stage_1_detected']:
                print("Detected Signals:")
                for flag in results['flags']:
                    signal = results['signals'][flag]
                    print(f"\n  • {flag.upper().replace('_', ' ')}")
                    if 'details' in signal:
                        for key, value in signal['details'].items():
                            if isinstance(value, float):
                                print(f"    - {key}: {value:.4f}")
                            else:
                                print(f"    - {key}: {value}")
            
            print("\n" + "="*70 + "\n")
        
        # Exit with appropriate code
        sys.exit(0 if not results['stage_1_detected'] else 1)
        
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
