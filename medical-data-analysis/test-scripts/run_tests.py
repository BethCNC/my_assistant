#!/usr/bin/env python3
"""
Medical Data Pipeline Test Runner

This script runs both the vector database check and the full pipeline test
to verify the system is working correctly.
"""

import os
import sys
import time
import logging
import subprocess
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_test_script(script_name):
    """Run a test script and return the result."""
    logger.info(f"Running test script: {script_name}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=False,
            capture_output=True,
            text=True
        )
        
        # Log the output
        for line in result.stdout.splitlines():
            logger.info(f"  {line}")
        
        # Log any errors
        if result.stderr:
            for line in result.stderr.splitlines():
                logger.error(f"  {line}")
        
        if result.returncode == 0:
            logger.info(f"Test script {script_name} passed successfully")
            return True
        else:
            logger.error(f"Test script {script_name} failed with exit code {result.returncode}")
            return False
            
    except Exception as e:
        logger.error(f"Error running test script {script_name}: {e}")
        return False

def run_all_tests():
    """Run all test scripts in order."""
    # Make sure test scripts exist
    test_scripts = ["check_vector_db.py", "test_pipeline.py"]
    
    for script in test_scripts:
        if not Path(script).exists():
            logger.error(f"Test script {script} not found")
            return False
    
    # Run vector database check first
    logger.info("Starting vector database check...")
    vector_db_success = run_test_script("check_vector_db.py")
    
    if not vector_db_success:
        logger.error("Vector database check failed. Stopping tests.")
        return False
    
    # Add a short delay between tests
    time.sleep(1)
    
    # Run full pipeline test
    logger.info("Starting full pipeline test...")
    pipeline_success = run_test_script("test_pipeline.py")
    
    # Overall success
    return vector_db_success and pipeline_success

if __name__ == "__main__":
    logger.info("=== Medical Data Pipeline Test Runner ===")
    
    success = run_all_tests()
    
    if success:
        logger.info("All tests completed successfully ✓")
        sys.exit(0)
    else:
        logger.error("Some tests failed ✗")
        sys.exit(1) 