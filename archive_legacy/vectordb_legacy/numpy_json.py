"""
NumPy JSON Serialization Module

Provides utilities for serializing NumPy arrays to JSON format and back.
This is used by the vector database components to store embeddings.
"""

import json
import numpy as np
from typing import Any

class NumpyEncoder(json.JSONEncoder):
    """JSON encoder that handles numpy arrays by converting them to lists."""
    
    def default(self, obj: Any) -> Any:
        """Convert numpy arrays and types to their Python equivalents."""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)

def loads_numpy(json_str: str) -> Any:
    """
    Load JSON string with NumPy array conversion.
    
    Args:
        json_str: JSON string to load
        
    Returns:
        Loaded Python object with lists that were originally NumPy arrays
    """
    return json.loads(json_str)

def dumps_numpy(obj: Any, **kwargs) -> str:
    """
    Dump object to JSON string with NumPy array conversion.
    
    Args:
        obj: Object to serialize
        **kwargs: Additional arguments to pass to json.dumps
        
    Returns:
        JSON string
    """
    return json.dumps(obj, cls=NumpyEncoder, **kwargs) 