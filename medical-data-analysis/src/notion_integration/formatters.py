"""
Formatters for converting data to and from Notion formats.
"""
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date

def format_title(value: str) -> Dict[str, Any]:
    """
    Format a string as a Notion title property.

    Args:
        value: The string value

    Returns:
        Formatted title property
    """
    return {
        "title": [
            {
                "text": {
                    "content": value
                }
            }
        ]
    }

def format_rich_text(value: str) -> Dict[str, Any]:
    """
    Format a string as a Notion rich text property.

    Args:
        value: The string value

    Returns:
        Formatted rich text property
    """
    return {
        "rich_text": [
            {
                "text": {
                    "content": str(value)
                }
            }
        ]
    }

def format_date(value: Union[str, datetime, date]) -> Dict[str, Any]:
    """
    Format a date as a Notion date property.

    Args:
        value: Date string (YYYY-MM-DD) or datetime object

    Returns:
        Formatted date property
    """
    if isinstance(value, (datetime, date)):
        date_str = value.isoformat().split('T')[0]
    else:
        date_str = value

    return {
        "date": {
            "start": date_str,
            "end": None
        }
    }

def format_number(value: Union[int, float]) -> Dict[str, Any]:
    """
    Format a number as a Notion number property.

    Args:
        value: Numeric value

    Returns:
        Formatted number property
    """
    return {
        "number": value
    }

def format_checkbox(value: bool) -> Dict[str, Any]:
    """
    Format a boolean as a Notion checkbox property.

    Args:
        value: Boolean value

    Returns:
        Formatted checkbox property
    """
    return {
        "checkbox": bool(value)
    }

def format_select(value: str) -> Dict[str, Any]:
    """
    Format a string as a Notion select property.

    Args:
        value: String value matching a select option

    Returns:
        Formatted select property
    """
    return {
        "select": {
            "name": value
        }
    }

def format_multi_select(values: List[str]) -> Dict[str, Any]:
    """
    Format a list of strings as a Notion multi-select property.

    Args:
        values: List of string values matching multi-select options

    Returns:
        Formatted multi-select property
    """
    return {
        "multi_select": [{"name": value} for value in values]
    }

def format_relation(page_ids: Union[str, List[str]]) -> Dict[str, Any]:
    """
    Format page IDs as a Notion relation property.

    Args:
        page_ids: Single page ID or list of page IDs

    Returns:
        Formatted relation property
    """
    if isinstance(page_ids, str):
        page_ids = [page_ids]

    return {
        "relation": [{"id": page_id} for page_id in page_ids]
    }

def extract_title(properties: Dict[str, Any], property_name: str) -> str:
    """
    Extract a title value from Notion properties.

    Args:
        properties: Notion properties object
        property_name: Name of the title property

    Returns:
        Extracted title string or empty string if not found
    """
    if property_name not in properties:
        return ""

    title_obj = properties[property_name]
    if not title_obj.get("title"):
        return ""

    titles = [t.get("text", {}).get("content", "") for t in title_obj.get("title", [])]
    return " ".join(titles).strip()

def extract_rich_text(properties: Dict[str, Any], property_name: str) -> str:
    """
    Extract a rich text value from Notion properties.

    Args:
        properties: Notion properties object
        property_name: Name of the rich text property

    Returns:
        Extracted text string or empty string if not found
    """
    if property_name not in properties:
        return ""

    text_obj = properties[property_name]
    if not text_obj.get("rich_text"):
        return ""

    texts = [t.get("text", {}).get("content", "") for t in text_obj.get("rich_text", [])]
    return " ".join(texts).strip()

def extract_date(properties: Dict[str, Any], property_name: str) -> Optional[str]:
    """
    Extract a date value from Notion properties.

    Args:
        properties: Notion properties object
        property_name: Name of the date property

    Returns:
        Extracted date string (YYYY-MM-DD) or None if not found
    """
    if property_name not in properties:
        return None

    date_obj = properties[property_name]
    return date_obj.get("date", {}).get("start")

def extract_number(properties: Dict[str, Any], property_name: str) -> Optional[float]:
    """
    Extract a number value from Notion properties.

    Args:
        properties: Notion properties object
        property_name: Name of the number property

    Returns:
        Extracted number or None if not found
    """
    if property_name not in properties:
        return None

    number_obj = properties[property_name]
    return number_obj.get("number")

def extract_checkbox(properties: Dict[str, Any], property_name: str) -> bool:
    """
    Extract a checkbox value from Notion properties.

    Args:
        properties: Notion properties object
        property_name: Name of the checkbox property

    Returns:
        Extracted boolean value or False if not found
    """
    if property_name not in properties:
        return False

    checkbox_obj = properties[property_name]
    return checkbox_obj.get("checkbox", False)

def extract_select(properties: Dict[str, Any], property_name: str) -> Optional[str]:
    """
    Extract a select value from Notion properties.

    Args:
        properties: Notion properties object
        property_name: Name of the select property

    Returns:
        Extracted select value or None if not found
    """
    if property_name not in properties:
        return None

    select_obj = properties[property_name]
    select_value = select_obj.get("select")
    if not select_value:
        return None

    return select_value.get("name")

def extract_multi_select(properties: Dict[str, Any], property_name: str) -> List[str]:
    """
    Extract multi-select values from Notion properties.

    Args:
        properties: Notion properties object
        property_name: Name of the multi-select property

    Returns:
        List of extracted multi-select values or empty list if not found
    """
    if property_name not in properties:
        return []

    multi_select_obj = properties[property_name]
    options = multi_select_obj.get("multi_select", [])
    return [option.get("name", "") for option in options if "name" in option]

def extract_relation_ids(properties: Dict[str, Any], property_name: str) -> List[str]:
    """
    Extract relation IDs from Notion properties.

    Args:
        properties: Notion properties object
        property_name: Name of the relation property

    Returns:
        List of related page IDs or empty list if not found
    """
    if property_name not in properties:
        return []

    relation_obj = properties[property_name]
    relations = relation_obj.get("relation", [])
    return [relation.get("id", "") for relation in relations if "id" in relation] 