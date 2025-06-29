#!/usr/bin/env python3
"""
Medical Data Pipeline Unit Test Runner

This script runs all unit tests for the medical data processing pipeline.
"""

import os
import sys
import unittest
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def discover_and_run_tests():
    """Discover and run all tests in the tests directory."""
    logger.info("Starting unit test discovery...")
    
    # Get the test directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_dir = os.path.join(current_dir, "src", "tests")
    
    if not os.path.exists(test_dir):
        logger.error(f"Test directory not found: {test_dir}")
        return False
    
    # Discover tests
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern="test_*.py")
    
    # Count test files and test cases
    test_files = {file for file in os.listdir(test_dir) if file.startswith("test_") and file.endswith(".py")}
    logger.info(f"Discovered {len(test_files)} test files in {test_dir}")
    
    # List all test files
    for test_file in sorted(test_files):
        logger.info(f"  - {test_file}")
    
    # Create a test runner
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Run the tests
    logger.info("Running tests...")
    result = runner.run(suite)
    
    # Report results
    logger.info(f"Tests completed: {result.testsRun} run, {len(result.errors)} errors, {len(result.failures)} failures")
    
    # Return success or failure
    return len(result.errors) + len(result.failures) == 0

if __name__ == "__main__":
    logger.info("=== Medical Data Pipeline Unit Test Runner ===")
    
    success = discover_and_run_tests()
    
    if success:
        logger.info("All tests passed successfully ✓")
        sys.exit(0)
    else:
        logger.error("Some tests failed ✗")
        sys.exit(1) 