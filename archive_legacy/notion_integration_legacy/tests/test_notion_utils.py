#!/usr/bin/env python3
"""
Unit tests for the notion_utils module
"""

import sys
import os
import unittest
from datetime import datetime, date
from pathlib import Path

# Add parent directory to path for imports
script_dir = Path(__file__).resolve().parent
sys.path.append(str(script_dir.parent.parent))

from notion_integration.notion_utils import (
    format_date_for_notion,
    format_rich_text_for_notion,
    format_select_for_notion,
    format_multi_select_for_notion,
    format_relation_for_notion,
    format_number_for_notion,
    format_url_for_notion,
    format_title_for_notion,
    get_notion_property_value
)


class TestNotionUtils(unittest.TestCase):
    """Test cases for the notion_utils module"""
    
    def test_format_date_for_notion(self):
        """Test formatting date values for Notion API"""
        # Test with date object
        today = date.today()
        expected = {"start": today.isoformat()}
        self.assertEqual(format_date_for_notion(today), expected)
        
        # Test with datetime object
        now = datetime.now()
        expected = {"start": now.isoformat()}
        self.assertEqual(format_date_for_notion(now), expected)
        
        # Test with ISO format string
        date_str = "2023-05-15"
        expected = {"start": date_str}
        self.assertEqual(format_date_for_notion(date_str), expected)
        
        # Test with range (end date as string)
        date_range = {"start": today, "end": "2023-12-31"}
        expected = {"start": today.isoformat(), "end": "2023-12-31"}
        self.assertEqual(format_date_for_notion(date_range), expected)
    
    def test_format_rich_text_for_notion(self):
        """Test formatting rich text for Notion API"""
        # Test simple text
        text = "Test content"
        expected = [{"type": "text", "text": {"content": text}}]
        self.assertEqual(format_rich_text_for_notion(text), expected)
        
        # Test with annotations
        text = "Test content"
        annotations = {"bold": True, "italic": True}
        expected = [{"type": "text", "text": {"content": text}, "annotations": annotations}]
        self.assertEqual(format_rich_text_for_notion(text, annotations), expected)
        
        # Test with URL
        text = "Test link"
        url = "https://example.com"
        expected = [{"type": "text", "text": {"content": text, "link": {"url": url}}}]
        self.assertEqual(format_rich_text_for_notion(text, url=url), expected)
        
    def test_format_select_for_notion(self):
        """Test formatting select values for Notion API"""
        option = "In Progress"
        expected = {"name": option}
        self.assertEqual(format_select_for_notion(option), expected)
        
        # Test with None value
        self.assertIsNone(format_select_for_notion(None))
        
        # Test with empty string
        self.assertIsNone(format_select_for_notion(""))
    
    def test_format_multi_select_for_notion(self):
        """Test formatting multi-select values for Notion API"""
        options = ["Tag 1", "Tag 2", "Tag 3"]
        expected = [{"name": "Tag 1"}, {"name": "Tag 2"}, {"name": "Tag 3"}]
        self.assertEqual(format_multi_select_for_notion(options), expected)
        
        # Test with empty list
        self.assertEqual(format_multi_select_for_notion([]), [])
        
        # Test with None
        self.assertEqual(format_multi_select_for_notion(None), [])
    
    def test_format_relation_for_notion(self):
        """Test formatting relation values for Notion API"""
        # Test with single ID
        page_id = "12345678-1234-1234-1234-123456789012"
        expected = [{"id": page_id}]
        self.assertEqual(format_relation_for_notion(page_id), expected)
        
        # Test with list of IDs
        page_ids = [
            "12345678-1234-1234-1234-123456789012",
            "87654321-4321-4321-4321-210987654321"
        ]
        expected = [{"id": page_ids[0]}, {"id": page_ids[1]}]
        self.assertEqual(format_relation_for_notion(page_ids), expected)
        
        # Test with empty input
        self.assertEqual(format_relation_for_notion([]), [])
        self.assertEqual(format_relation_for_notion(None), [])
    
    def test_format_number_for_notion(self):
        """Test formatting number values for Notion API"""
        # Test with integer
        self.assertEqual(format_number_for_notion(42), 42)
        
        # Test with float
        self.assertEqual(format_number_for_notion(3.14), 3.14)
        
        # Test with string that can be converted to number
        self.assertEqual(format_number_for_notion("42"), 42)
        self.assertEqual(format_number_for_notion("3.14"), 3.14)
        
        # Test with None
        self.assertIsNone(format_number_for_notion(None))
        
        # Test with non-numeric string
        with self.assertRaises(ValueError):
            format_number_for_notion("not a number")
    
    def test_format_url_for_notion(self):
        """Test formatting URL values for Notion API"""
        url = "https://example.com"
        self.assertEqual(format_url_for_notion(url), url)
        
        # Test with None
        self.assertIsNone(format_url_for_notion(None))
        
        # Test with empty string
        self.assertIsNone(format_url_for_notion(""))
    
    def test_format_title_for_notion(self):
        """Test formatting title values for Notion API"""
        title = "Test Title"
        expected = [{"type": "text", "text": {"content": title}}]
        self.assertEqual(format_title_for_notion(title), expected)
        
        # Test with None
        self.assertEqual(format_title_for_notion(None), [])
        
        # Test with empty string
        self.assertEqual(format_title_for_notion(""), [])
    
    def test_get_notion_property_value(self):
        """Test extracting values from Notion properties"""
        # Test title property
        title_prop = {
            "type": "title",
            "title": [{"type": "text", "text": {"content": "Test Title"}}]
        }
        self.assertEqual(get_notion_property_value(title_prop), "Test Title")
        
        # Test rich text property
        rich_text_prop = {
            "type": "rich_text",
            "rich_text": [{"type": "text", "text": {"content": "Test Content"}}]
        }
        self.assertEqual(get_notion_property_value(rich_text_prop), "Test Content")
        
        # Test date property
        date_prop = {
            "type": "date",
            "date": {"start": "2023-05-15", "end": None}
        }
        self.assertEqual(get_notion_property_value(date_prop), {"start": "2023-05-15", "end": None})
        
        # Test select property
        select_prop = {
            "type": "select",
            "select": {"name": "Option 1", "id": "12345"}
        }
        self.assertEqual(get_notion_property_value(select_prop), "Option 1")
        
        # Test multi-select property
        multi_select_prop = {
            "type": "multi_select",
            "multi_select": [
                {"name": "Tag 1", "id": "12345"},
                {"name": "Tag 2", "id": "67890"}
            ]
        }
        self.assertEqual(get_notion_property_value(multi_select_prop), ["Tag 1", "Tag 2"])
        
        # Test number property
        number_prop = {
            "type": "number",
            "number": 42
        }
        self.assertEqual(get_notion_property_value(number_prop), 42)
        
        # Test checkbox property
        checkbox_prop = {
            "type": "checkbox",
            "checkbox": True
        }
        self.assertEqual(get_notion_property_value(checkbox_prop), True)
        
        # Test relation property
        relation_prop = {
            "type": "relation",
            "relation": [
                {"id": "12345678-1234-1234-1234-123456789012"},
                {"id": "87654321-4321-4321-4321-210987654321"}
            ]
        }
        expected = ["12345678-1234-1234-1234-123456789012", "87654321-4321-4321-4321-210987654321"]
        self.assertEqual(get_notion_property_value(relation_prop), expected)
        
        # Test unsupported property type
        unsupported_prop = {
            "type": "unsupported",
            "unsupported": "value"
        }
        self.assertIsNone(get_notion_property_value(unsupported_prop))


if __name__ == "__main__":
    unittest.main() 