"""
Configuration Module

This module provides configuration management for the medical data to Notion integration.
It handles loading and validation of configuration settings from files or environment.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_CONFIG = {
    "openai": {
        "api_key": "",
        "model": "gpt-4o",
        "temperature": 0.1,
        "max_tokens": 2048
    },
    "notion": {
        "token": "",
        "databases": {
            "medical_calendar": "",
            "medical_team": "",
            "medical_conditions": "",
            "medications": "",
            "symptoms": ""
        }
    },
    "extraction": {
        "chunk_size": 4000,
        "chunk_overlap": 200,
        "minimum_confidence": 0.7
    },
    "processing": {
        "file_types": [".pdf", ".txt", ".html", ".csv", ".md"],
        "data_dir": "data",
        "output_dir": "processed_data",
        "max_workers": 4
    }
}


class ConfigManager:
    """Configuration manager for the application"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager
        
        Args:
            config_path: Path to the configuration file (JSON)
                         If None, will attempt to load from environment variables
        """
        self.config = DEFAULT_CONFIG.copy()
        
        # Load from file if provided
        if config_path and os.path.exists(config_path):
            self._load_from_file(config_path)
        
        # Override with environment variables (takes precedence over file)
        self._load_from_environment()
        
        # Validate the configuration
        self._validate_config()
    
    def _load_from_file(self, config_path: str) -> None:
        """
        Load configuration from a JSON file
        
        Args:
            config_path: Path to the configuration file
        """
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                
            # Merge with existing config (deep merge)
            self._deep_merge(self.config, file_config)
            logger.info(f"Loaded configuration from {config_path}")
            
        except Exception as e:
            logger.error(f"Error loading configuration from {config_path}: {str(e)}")
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables"""
        # OpenAI settings
        if os.environ.get('OPENAI_API_KEY'):
            self.config['openai']['api_key'] = os.environ.get('OPENAI_API_KEY')
        
        if os.environ.get('OPENAI_MODEL'):
            self.config['openai']['model'] = os.environ.get('OPENAI_MODEL')
        
        # Notion settings
        if os.environ.get('NOTION_TOKEN'):
            self.config['notion']['token'] = os.environ.get('NOTION_TOKEN')
            
        # Notion database IDs
        for db_type in self.config['notion']['databases'].keys():
            env_var = f"NOTION_{db_type.upper()}_DB"
            if os.environ.get(env_var):
                self.config['notion']['databases'][db_type] = os.environ.get(env_var)
    
    def _deep_merge(self, target: Dict, source: Dict) -> None:
        """
        Deep merge source dictionary into target
        
        Args:
            target: Target dictionary to merge into
            source: Source dictionary to merge from
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                self._deep_merge(target[key], value)
            else:
                # Overwrite or add value
                target[key] = value
    
    def _validate_config(self) -> None:
        """Validate the configuration and log warnings for missing critical values"""
        critical_missing = []
        
        # Check for critical API keys
        if not self.config['openai']['api_key']:
            critical_missing.append("OpenAI API key")
        
        if not self.config['notion']['token']:
            critical_missing.append("Notion token")
        
        # Check for at least one database ID
        has_db = False
        for db_type, db_id in self.config['notion']['databases'].items():
            if db_id:
                has_db = True
                break
                
        if not has_db:
            critical_missing.append("At least one Notion database ID")
        
        # Log warnings for missing values
        if critical_missing:
            logger.warning(f"Missing critical configuration values: {', '.join(critical_missing)}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key
        
        Args:
            key: Dot-separated key path (e.g., 'openai.api_key')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        parts = key.split('.')
        config = self.config
        
        for part in parts:
            if isinstance(config, dict) and part in config:
                config = config[part]
            else:
                return default
                
        return config
    
    def get_databases(self) -> Dict[str, str]:
        """
        Get a dictionary of database types to database IDs
        
        Returns:
            Dictionary mapping database types to Notion database IDs
        """
        return {k: v for k, v in self.config['notion']['databases'].items() if v}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Get the entire configuration as a dictionary
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()
    
    def save_to_file(self, file_path: str) -> None:
        """
        Save the current configuration to a JSON file
        
        Args:
            file_path: Path to save the configuration
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            with open(file_path, 'w') as f:
                json.dump(self.config, f, indent=2)
                
            logger.info(f"Saved configuration to {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving configuration to {file_path}: {str(e)}")


def create_default_config(file_path: str) -> None:
    """
    Create a default configuration file
    
    Args:
        file_path: Path to save the default configuration
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
            
        logger.info(f"Created default configuration at {file_path}")
        
    except Exception as e:
        logger.error(f"Error creating default configuration at {file_path}: {str(e)}") 