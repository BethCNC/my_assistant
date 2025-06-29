# Medical Data Pipeline Tests

This directory contains the test suite for the medical data processing pipeline. The tests are organized into several modules that test different components of the system.

## Test Structure

- `test_extraction.py`: Tests for document extraction components
- `test_vector_db.py`: Tests for vector database and embedding functionality
- `test_ingestion_pipeline.py`: Tests for the main ingestion pipeline
- `test_ai_processing.py`: Tests for AI and entity extraction components
- `test_clinical_data_extraction.py`: Tests for specialized clinical data extraction

## Test Configuration

The `test_config.py` file contains shared test constants, fixtures, and helper functions that are used across multiple test modules. This includes:

- Sample medical texts for testing
- Sample medical entities (conditions, symptoms, treatments)
- Helper functions for creating test environments
- Mock data generation functions

## Running Tests

You can run the tests in several ways:

### Run All Tests

To run all tests at once, use the `run_unit_tests.py` script from the project root directory:

```bash
python run_unit_tests.py
```

### Run Individual Test Modules

To run a specific test module, you can use Python's unittest directly:

```bash
python -m unittest src/tests/test_extraction.py
python -m unittest src/tests/test_vector_db.py
```

### Run with Coverage Report

To run tests with coverage reporting, use the following commands:

```bash
# Install coverage if not already installed
pip install coverage

# Run tests with coverage
coverage run run_unit_tests.py

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
```

## Writing New Tests

When adding new test modules, follow these guidelines:

1. Name test files with `test_` prefix
2. Use the unittest framework
3. Make tests independent and isolated
4. Clean up test resources in tearDown methods
5. Use the helper functions from `test_config.py` when possible
6. Mock external dependencies

### Test Module Template

```python
import sys
import os
import unittest
import tempfile
from pathlib import Path

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import from test_config for shared fixtures and helpers
from src.tests.test_config import (
    create_temp_test_dir, cleanup_test_dir, mock_extraction_result
)

# Import the module to test
from src.module.to_test import ComponentToTest

class TestComponentName(unittest.TestCase):
    """Test suite for [component name]."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = create_temp_test_dir()
        # Additional setup

    def test_functionality(self):
        """Test specific functionality."""
        # Test implementation

    def tearDown(self):
        """Clean up test environment."""
        cleanup_test_dir(self.test_dir)

if __name__ == "__main__":
    unittest.main() 