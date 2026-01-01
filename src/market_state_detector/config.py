"""
Configuration management for market state detector.

This module handles loading and validating configuration settings for the
market state detection system. Configuration can be loaded from YAML files
or provided programmatically.
"""

import os
import copy
from typing import Any, Dict, Optional
import yaml


class Config:
    """
    Configuration manager for market state detector.
    
    This class handles loading configuration from YAML files and provides
    default values for all detection parameters.
    
    Attributes:
        volatility_threshold: Multiplier for detecting volatility spikes
        gap_threshold_percent: Minimum gap size as percentage to flag
        range_threshold_percent: Minimum range expansion to flag
        lookback_period: Number of days to analyze for baseline
        min_data_points: Minimum data points required for analysis
    """
    
    DEFAULT_CONFIG = {
        "volatility": {
            "threshold_multiplier": 2.0,
            "lookback_period": 20,
        },
        "gaps": {
            "threshold_percent": 2.0,
        },
        "ranges": {
            "threshold_percent": 50.0,
            "lookback_period": 20,
        },
        "general": {
            "min_data_points": 21,
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to YAML configuration file. If None, uses defaults.
        """
        self.config = copy.deepcopy(self.DEFAULT_CONFIG)
        
        if config_path and os.path.exists(config_path):
            self.load_from_file(config_path)
    
    def load_from_file(self, path: str) -> None:
        """
        Load configuration from YAML file.
        
        Args:
            path: Path to YAML configuration file
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid YAML
        """
        with open(path, 'r') as f:
            user_config = yaml.safe_load(f)
            if user_config:
                self._merge_config(user_config)
    
    def _merge_config(self, user_config: Dict[str, Any]) -> None:
        """
        Merge user configuration with defaults.
        
        Args:
            user_config: User-provided configuration dictionary
        """
        for section, values in user_config.items():
            if section in self.config and isinstance(values, dict):
                self.config[section].update(values)
            else:
                self.config[section] = values
    
    def get(self, section: str, key: str) -> Any:
        """
        Get configuration value.
        
        Args:
            section: Configuration section name
            key: Configuration key within section
            
        Returns:
            Configuration value
            
        Raises:
            KeyError: If section or key doesn't exist
        """
        return self.config[section][key]
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section.
        
        Args:
            section: Configuration section name
            
        Returns:
            Dictionary of configuration values for the section
        """
        return self.config.get(section, {})
