"""
Notion Utils

This module provides utility functions for working with Notion properties,
formatting data, and handling special cases.
"""

import logging
from typing import Dict, List, Any, Optional, Union, TypedDict, cast
from datetime import datetime, date
import re

logger = logging.getLogger(__name__)


class DateRange(TypedDict, total=False):
    """Type definition for date range objects"""
    start: Union[str, datetime, date]
    end: Optional[Union[str, datetime, date]]


def format_date_for_notion(date_value: Union[str, datetime, date, DateRange]) -> Dict[str, Any]:
    """
    Format a date value for Notion API
    
    Args:
        date_value: Date string, datetime object, or date range dict
        
    Returns:
        Notion-formatted date object
    """
    # Handle date range dict
    if isinstance(date_value, dict):
        result = {}
        if "start" in date_value:
            start_date = date_value["start"]
            if isinstance(start_date, (datetime, date)):
                result["start"] = start_date.isoformat()
            else:
                result["start"] = start_date
                
        if "end" in date_value and date_value["end"]:
            end_date = date_value["end"]
            if isinstance(end_date, (datetime, date)):
                result["end"] = end_date.isoformat()
            else:
                result["end"] = end_date
                
        return result
    
    # Handle string, date or datetime
    if isinstance(date_value, str):
        return {"start": date_value}
    
    # Handle datetime or date
    return {"start": date_value.isoformat()}


def format_rich_text_for_notion(
    text: str, 
    annotations: Optional[Dict[str, Any]] = None, 
    url: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Format rich text content for Notion API
    
    Args:
        text: Text content
        annotations: Optional text annotations (bold, italic, etc.)
        url: Optional URL for the text
        
    Returns:
        Notion-formatted rich text array
    """
    if not text:
        return []
    
    rich_text = {
        "type": "text",
        "text": {"content": text}
    }
    
    if url:
        rich_text["text"]["link"] = {"url": url}
        
    if annotations:
        rich_text["annotations"] = annotations
        
    return [rich_text]


def format_select_for_notion(option: Optional[str]) -> Optional[Dict[str, str]]:
    """
    Format select option for Notion API
    
    Args:
        option: Option name
        
    Returns:
        Notion-formatted select object or None
    """
    if not option:
        return None
        
    return {"name": option}


def format_multi_select_for_notion(options: Optional[List[str]]) -> List[Dict[str, str]]:
    """
    Format multi-select options for Notion API
    
    Args:
        options: List of option names
        
    Returns:
        Notion-formatted multi-select array
    """
    if not options:
        return []
        
    return [{"name": option} for option in options]


def format_relation_for_notion(page_ids: Union[str, List[str], None]) -> List[Dict[str, str]]:
    """
    Format relation for Notion API
    
    Args:
        page_ids: Single page ID or list of page IDs
        
    Returns:
        Notion-formatted relation array
    """
    if not page_ids:
        return []
        
    if isinstance(page_ids, str):
        return [{"id": page_ids}]
        
    return [{"id": page_id} for page_id in page_ids]


def format_number_for_notion(value: Union[int, float, str, None]) -> Optional[Union[int, float]]:
    """
    Format number for Notion API
    
    Args:
        value: Number value
        
    Returns:
        Integer or float, or None if value is empty
    """
    if value is None:
        return None
        
    if isinstance(value, (int, float)):
        return value
        
    # Try to convert string to number
    if isinstance(value, str) and value:
        try:
            # Try to convert to int first
            if value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
                return int(value)
            # If that fails, try float
            return float(value)
        except ValueError:
            raise ValueError(f"Cannot convert value to number: {value}")
            
    return None


def format_url_for_notion(url: Optional[str]) -> Optional[str]:
    """
    Format URL for Notion API
    
    Args:
        url: URL string
        
    Returns:
        URL string or None if empty
    """
    if not url:
        return None
        
    return url


def format_title_for_notion(title: Optional[str]) -> List[Dict[str, Any]]:
    """
    Format title for Notion API
    
    Args:
        title: Title string
        
    Returns:
        Notion-formatted title array
    """
    if not title:
        return []
        
    return [{"type": "text", "text": {"content": title}}]


def get_notion_property_value(property_data: Dict[str, Any]) -> Any:
    """
    Extract the value from a Notion property
    
    Args:
        property_data: Notion property object
        
    Returns:
        Extracted value
    """
    property_type = property_data.get("type")
    
    if property_type == "title":
        title = property_data.get("title", [])
        if not title:
            return ""
        return "".join([text_obj.get("text", {}).get("content", "") for text_obj in title])
        
    elif property_type == "rich_text":
        rich_text = property_data.get("rich_text", [])
        if not rich_text:
            return ""
        return "".join([text_obj.get("text", {}).get("content", "") for text_obj in rich_text])
        
    elif property_type == "date":
        return property_data.get("date")
        
    elif property_type == "select":
        select = property_data.get("select")
        if not select:
            return None
        return select.get("name")
        
    elif property_type == "multi_select":
        multi_select = property_data.get("multi_select", [])
        return [option.get("name") for option in multi_select]
        
    elif property_type == "number":
        return property_data.get("number")
        
    elif property_type == "checkbox":
        return property_data.get("checkbox")
        
    elif property_type == "url":
        return property_data.get("url")
        
    elif property_type == "email":
        return property_data.get("email")
        
    elif property_type == "phone_number":
        return property_data.get("phone_number")
        
    elif property_type == "relation":
        relation = property_data.get("relation", [])
        return [rel.get("id") for rel in relation]
        
    # Return None for unsupported property types
    return None


def create_property_object(property_name: str, property_value: Any, property_type: str) -> Dict[str, Any]:
    """
    Create a Notion property object with value of specified type
    
    Args:
        property_name: Name of the property
        property_value: Value of the property
        property_type: Type of the property
        
    Returns:
        Notion property object
    """
    # Skip empty values
    if property_value is None:
        return {}
        
    if property_type == "title":
        return {property_name: {"title": format_title_for_notion(property_value)}}
        
    elif property_type == "rich_text":
        return {property_name: {"rich_text": format_rich_text_for_notion(property_value)}}
        
    elif property_type == "date":
        return {property_name: {"date": format_date_for_notion(property_value)}}
        
    elif property_type == "select":
        select_value = format_select_for_notion(property_value)
        if select_value:
            return {property_name: {"select": select_value}}
        return {}
        
    elif property_type == "multi_select":
        return {property_name: {"multi_select": format_multi_select_for_notion(property_value)}}
        
    elif property_type == "number":
        number_value = format_number_for_notion(property_value)
        if number_value is not None:
            return {property_name: {"number": number_value}}
        return {}
        
    elif property_type == "checkbox":
        return {property_name: {"checkbox": bool(property_value)}}
        
    elif property_type == "url":
        url_value = format_url_for_notion(property_value)
        if url_value:
            return {property_name: {"url": url_value}}
        return {}
        
    elif property_type == "email":
        if property_value:
            return {property_name: {"email": property_value}}
        return {}
        
    elif property_type == "phone_number":
        if property_value:
            return {property_name: {"phone_number": property_value}}
        return {}
        
    elif property_type == "relation":
        return {property_name: {"relation": format_relation_for_notion(property_value)}}
        
    # Return empty dict for unsupported property types
    logger.warning(f"Unsupported property type: {property_type}")
    return {}


def format_notion_property(value: Any, property_type: str) -> Optional[Dict[str, Any]]:
    """
    Format a value according to Notion property type
    
    Args:
        value: The value to format
        property_type: Notion property type
        
    Returns:
        Formatted property value ready for Notion API, or None if not formattable
    """
    if value is None:
        return None
        
    if property_type == "title":
        return {"title": [{"text": {"content": str(value)}}]}
    
    elif property_type == "rich_text":
        return {"rich_text": [{"text": {"content": str(value)}}]}
    
    elif property_type == "number":
        # Handle various number formats with explicit type checking
        try:
            # For numeric types (int, float)
            if isinstance(value, (int, float)):
                number_prop = format_number_for_notion(value)
            # For string representations of numbers
            elif isinstance(value, str):
                number_prop = format_number_for_notion(value)
            # For lists, try to use the first item
            elif isinstance(value, list) and value:
                if isinstance(value[0], (int, float, str)):
                    number_prop = format_number_for_notion(value[0])
                else:
                    number_prop = format_number_for_notion(str(value[0]))
            # For other types, try to convert to string first
            else:
                number_prop = format_number_for_notion(str(value))
            
            if number_prop is not None:
                return {"number": number_prop}
        except Exception as e:
            logger.warning(f"Could not format number for {property_type}: {e}")
            return {"number": None}
    
    elif property_type == "select":
        return {"select": {"name": str(value)} if value else None}
    
    elif property_type == "multi_select":
        if isinstance(value, list):
            return {"multi_select": [{"name": str(item)} for item in value if item]}
        elif isinstance(value, str):
            # Split comma-separated values
            items = [item.strip() for item in value.split(",") if item.strip()]
            return {"multi_select": [{"name": item} for item in items]}
        else:
            return {"multi_select": []}
    
    elif property_type == "date":
        # Handle various date formats with explicit type checking
        try:
            # For datetime or date objects
            if isinstance(value, (datetime, date)):
                date_prop = format_date_for_notion(value)
            # For string representations of dates
            elif isinstance(value, str):
                date_prop = format_date_for_notion(value)
            # For lists, try to use the first item
            elif isinstance(value, list) and value and (isinstance(value[0], (str, datetime, date))):
                date_prop = format_date_for_notion(value[0])
            # For other types, convert to string and try to parse
            else:
                date_prop = format_date_for_notion(str(value))
            
            if date_prop:
                return date_prop
        except Exception as e:
            logger.warning(f"Could not format date for {property_type}: {e}")
            return None
    
    elif property_type == "checkbox":
        # Handle various checkbox formats with explicit type checking
        try:
            # For boolean values
            if isinstance(value, bool):
                checkbox_prop = format_checkbox(value)
            # For numeric values
            elif isinstance(value, int):
                checkbox_prop = format_checkbox(value)
            # For string representations
            elif isinstance(value, str):
                checkbox_prop = format_checkbox(value)
            # For lists, try to use the first item
            elif isinstance(value, list) and value:
                if isinstance(value[0], (bool, int, str)):
                    checkbox_prop = format_checkbox(value[0])
                else:
                    checkbox_prop = format_checkbox(str(value[0]))
            # For other types, default to False
            else:
                checkbox_prop = format_checkbox(False)
            
            if checkbox_prop:
                return checkbox_prop
        except Exception as e:
            logger.warning(f"Could not format checkbox for {property_type}: {e}")
            return None
    
    elif property_type == "url":
        return {"url": str(value) if value else None}
    
    elif property_type == "email":
        return {"email": str(value) if value else None}
    
    elif property_type == "phone_number":
        return {"phone_number": str(value) if value else None}
    
    elif property_type == "relation":
        if isinstance(value, list):
            return {"relation": [{"id": item} for item in value]}
        return {"relation": [{"id": str(value)}]} if value else {"relation": []}
    
    # Default case
    logger.warning(f"Unsupported property type: {property_type}")
    return None


def map_data_to_notion_properties(
    data: Dict[str, Any],
    property_map: Dict[str, Dict[str, str]]
) -> Dict[str, Dict[str, Any]]:
    """
    Map extracted data to Notion properties based on property map
    
    Args:
        data: Extracted data dictionary
        property_map: Dictionary mapping data keys to Notion properties
        
    Returns:
        Dictionary of Notion-formatted properties
    """
    notion_properties = {}
    
    for key, value in data.items():
        if key in property_map:
            prop_info = property_map[key]
            notion_key = prop_info.get("notion_key")
            prop_type = prop_info.get("property_type")
            
            if notion_key and prop_type:
                formatted_value = format_notion_property(value, prop_type)
                if formatted_value is not None:
                    notion_properties[notion_key] = formatted_value
    
    return notion_properties


def find_page_by_unique_property(
    notion_client,
    database_id: str,
    property_name: str,
    property_value: str
) -> Optional[str]:
    """
    Find a Notion page by a unique property value
    
    Args:
        notion_client: Notion API client
        database_id: ID of the Notion database
        property_name: Name of the property to search
        property_value: Value to search for
        
    Returns:
        Page ID if found, None otherwise
    """
    try:
        filter_condition = {
            "property": property_name,
            "rich_text": {
                "equals": property_value
            }
        }
        
        # Try text filter first
        response = notion_client.databases.query(
            database_id=database_id,
            filter=filter_condition
        )
        
        results = response.get("results", [])
        
        if not results:
            # Try title filter if text filter didn't work
            filter_condition = {
                "property": property_name,
                "title": {
                    "equals": property_value
                }
            }
            
            response = notion_client.databases.query(
                database_id=database_id,
                filter=filter_condition
            )
            
            results = response.get("results", [])
        
        if results:
            return results[0]["id"]
        
        return None
    
    except Exception as e:
        logger.error(f"Error finding page by property: {e}")
        return None


def format_title(text: str) -> Dict[str, Any]:
    """
    Format a title property for Notion.
    
    Args:
        text: The title text
        
    Returns:
        Formatted title property
    """
    if not text:
        text = "Untitled"
        
    return {
        "title": [
            {
                "type": "text",
                "text": {
                    "content": text
                }
            }
        ]
    }


def format_rich_text(text: str, max_length: int = 2000) -> Dict[str, Any]:
    """
    Format a rich text property for Notion, with truncation if necessary.
    
    Args:
        text: The text content
        max_length: Maximum character length (Notion limit is 2000 per block)
        
    Returns:
        Formatted rich text property
    """
    if not text:
        text = ""
    
    # Truncate if necessary
    if len(text) > max_length:
        text = text[:max_length - 3] + "..."
    
    return {
        "rich_text": [
            {
                "type": "text",
                "text": {
                    "content": text
                }
            }
        ]
    }


def format_date(date_value: Optional[Union[str, datetime, date]] = None) -> Optional[Dict[str, Any]]:
    """
    Format a date property for Notion.
    
    Args:
        date_value: The date value (string, datetime, or date object)
        
    Returns:
        Formatted date property or None if date_value is None
    """
    if date_value is None:
        return None
    
    date_str = ""
    
    if isinstance(date_value, str):
        date_str = date_value
    elif isinstance(date_value, (datetime, date)):
        date_str = date_value.isoformat()
    
    if not date_str:
        return None
    
    return {
        "date": {
            "start": date_str
        }
    }


def format_select(value: Optional[str], options: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
    """
    Format a select property for Notion.
    
    Args:
        value: The select value
        options: Valid options (not enforced by API, just for validation)
        
    Returns:
        Formatted select property or None if value is None or empty
    """
    if not value:
        return None
    
    # Validate against options if provided
    if options and value not in options:
        logger.warning(f"Select value '{value}' is not in options: {options}")
    
    return {
        "select": {
            "name": value
        }
    }


def format_multi_select(values: List[str], options: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Format a multi-select property for Notion.
    
    Args:
        values: The multi-select values
        options: Valid options (not enforced by API, just for validation)
        
    Returns:
        Formatted multi-select property
    """
    if not values:
        return {"multi_select": []}
    
    # Validate against options if provided
    if options:
        for value in values:
            if value not in options:
                logger.warning(f"Multi-select value '{value}' is not in options: {options}")
    
    return {
        "multi_select": [{"name": value} for value in values]
    }


def format_status(value: Optional[str], options: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
    """
    Format a status property for Notion.
    
    Args:
        value: The status value
        options: Valid options (not enforced by API, just for validation)
        
    Returns:
        Formatted status property or None if value is None or empty
    """
    if not value:
        return None
    
    # Validate against options if provided
    if options and value not in options:
        logger.warning(f"Status value '{value}' is not in options: {options}")
    
    return {
        "status": {
            "name": value
        }
    }


def format_number(value: Optional[Union[int, float, str]] = None) -> Optional[Dict[str, Any]]:
    """
    Format a number property for Notion.
    
    Args:
        value: The number value (int, float, or string representation)
        
    Returns:
        Formatted number property or None if value is None or not convertible to number
    """
    if value is None:
        return None
    
    number_value = None
    
    if isinstance(value, (int, float)):
        number_value = value
    elif isinstance(value, str) and value.strip():
        try:
            # Try to convert to number
            number_value = float(value)
            # If it's an integer value, convert to int
            if number_value.is_integer():
                number_value = int(number_value)
        except ValueError:
            logger.warning(f"Could not convert '{value}' to number")
            return None
    
    if number_value is None:
        return None
    
    return {
        "number": number_value
    }


def format_url(value: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Format a URL property for Notion.
    
    Args:
        value: The URL value
        
    Returns:
        Formatted URL property or None if value is None or empty
    """
    if not value:
        return None
    
    return {
        "url": value
    }


def format_email(value: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Format an email property for Notion.
    
    Args:
        value: The email value
        
    Returns:
        Formatted email property or None if value is None or empty
    """
    if not value:
        return None
    
    return {
        "email": value
    }


def format_phone_number(value: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Format a phone number property for Notion.
    
    Args:
        value: The phone number value
        
    Returns:
        Formatted phone number property or None if value is None or empty
    """
    if not value:
        return None
    
    return {
        "phone_number": value
    }


def format_relation(value: Optional[Union[str, List[str]]] = None) -> Dict[str, Any]:
    """
    Format a relation property for Notion.
    
    Args:
        value: The relation value(s) (page IDs)
        
    Returns:
        Formatted relation property
    """
    if not value:
        return {"relation": []}
    
    if isinstance(value, str):
        return {"relation": [{"id": value}]}
    
    return {"relation": [{"id": page_id} for page_id in value]}


def format_checkbox(value: Optional[Union[bool, str, int]] = None) -> Optional[Dict[str, Any]]:
    """
    Format a checkbox property for Notion.
    
    Args:
        value: The checkbox value (boolean, string, or int)
        
    Returns:
        Formatted checkbox property or None if value is None
    """
    if value is None:
        return None
    
    bool_value = False
    
    if isinstance(value, bool):
        bool_value = value
    elif isinstance(value, int):
        bool_value = bool(value)
    elif isinstance(value, str):
        bool_value = value.lower() in ("true", "yes", "y", "1", "on")
    
    return {
        "checkbox": bool_value
    }


def extract_date_from_text(text: str) -> Optional[str]:
    """
    Extract a date from text using regex patterns.
    
    Args:
        text: Text to extract date from
        
    Returns:
        ISO formatted date string (YYYY-MM-DD) or None if no date found
    """
    # Various date patterns
    patterns = [
        # ISO format: YYYY-MM-DD
        r'(\d{4}-\d{2}-\d{2})',
        # MM/DD/YYYY
        r'(\d{1,2}/\d{1,2}/\d{4})',
        # MM-DD-YYYY
        r'(\d{1,2}-\d{1,2}-\d{4})',
        # Month DD, YYYY
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            date_str = match.group(0)
            try:
                # Try to parse with datetime and convert to ISO
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                return dt.isoformat().split('T')[0]
            except ValueError:
                try:
                    dt = datetime.strptime(date_str, "%m/%d/%Y")
                    return dt.isoformat().split('T')[0]
                except ValueError:
                    try:
                        dt = datetime.strptime(date_str, "%m-%d-%Y")
                        return dt.isoformat().split('T')[0]
                    except ValueError:
                        try:
                            dt = datetime.strptime(date_str, "%B %d, %Y")
                            return dt.isoformat().split('T')[0]
                        except ValueError:
                            # If we can't parse it, just return the original string
                            return date_str
    
    return None


def format_notion_page_properties(properties_dict: Dict[str, Any], schema: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Format dictionary of values into Notion page properties based on schema.
    
    Args:
        properties_dict: Dictionary of property values
        schema: Notion database schema defining property types
        
    Returns:
        Dictionary of formatted Notion properties
    """
    formatted_properties = {}
    
    for prop_name, schema_info in schema.items():
        # Skip if property not in input dictionary
        if prop_name not in properties_dict:
            continue
        
        value = properties_dict[prop_name]
        prop_type = schema_info.get("type")
        
        # Skip empty values (None, empty strings, empty lists)
        if value is None or (isinstance(value, (str, list)) and not value):
            continue
        
        try:
            # Format based on property type
            if prop_type == "title":
                # Ensure value is a string
                str_value = str(value) if not isinstance(value, list) else ", ".join(str(v) for v in value)
                formatted_properties[prop_name] = format_title(str_value)
            
            elif prop_type == "rich_text":
                # Ensure value is a string
                str_value = str(value) if not isinstance(value, list) else ", ".join(str(v) for v in value)
                formatted_properties[prop_name] = format_rich_text(str_value)
            
            elif prop_type == "date":
                if isinstance(value, (datetime, date)):
                    date_prop = format_date(value)
                elif isinstance(value, str):
                    date_prop = format_date(value)
                elif isinstance(value, list) and value and isinstance(value[0], (str, datetime, date)):
                    date_prop = format_date(value[0])
                else:
                    date_prop = None
                
                if date_prop:
                    formatted_properties[prop_name] = date_prop
            
            elif prop_type == "select":
                # Ensure value is a string
                if isinstance(value, list) and value:
                    str_value = str(value[0])  # Take first item if list
                else:
                    str_value = str(value)
                
                select_prop = format_select(str_value, schema_info.get("options"))
                if select_prop:
                    formatted_properties[prop_name] = select_prop
            
            elif prop_type == "multi_select":
                # Ensure value is a list of strings
                if isinstance(value, list):
                    value_list = [str(v) for v in value]
                else:
                    value_list = [str(value)]
                
                formatted_properties[prop_name] = format_multi_select(value_list, schema_info.get("options"))
            
            elif prop_type == "status":
                # Ensure value is a string
                if isinstance(value, list) and value:
                    str_value = str(value[0])  # Take first item if list
                else:
                    str_value = str(value)
                
                status_prop = format_status(str_value, schema_info.get("options"))
                if status_prop:
                    formatted_properties[prop_name] = status_prop
            
            elif prop_type == "number":
                if isinstance(value, (int, float)):
                    number_prop = format_number(value)
                elif isinstance(value, str):
                    number_prop = format_number(value)
                elif isinstance(value, list) and value and isinstance(value[0], (int, float, str)):
                    number_prop = format_number(value[0])
                else:
                    number_prop = format_number(str(value))
                
                if number_prop:
                    formatted_properties[prop_name] = number_prop
            
            elif prop_type == "url":
                # Ensure value is a string
                if isinstance(value, list) and value:
                    str_value = str(value[0])  # Take first item if list
                else:
                    str_value = str(value)
                
                url_prop = format_url(str_value)
                if url_prop:
                    formatted_properties[prop_name] = url_prop
            
            elif prop_type == "email":
                # Ensure value is a string
                if isinstance(value, list) and value:
                    str_value = str(value[0])  # Take first item if list
                else:
                    str_value = str(value)
                
                email_prop = format_email(str_value)
                if email_prop:
                    formatted_properties[prop_name] = email_prop
            
            elif prop_type == "phone_number":
                # Ensure value is a string
                if isinstance(value, list) and value:
                    str_value = str(value[0])  # Take first item if list
                else:
                    str_value = str(value)
                
                phone_prop = format_phone_number(str_value)
                if phone_prop:
                    formatted_properties[prop_name] = phone_prop
            
            elif prop_type == "relation":
                formatted_properties[prop_name] = format_relation(value)
            
            elif prop_type == "checkbox":
                if isinstance(value, bool):
                    checkbox_prop = format_checkbox(value)
                elif isinstance(value, int):
                    checkbox_prop = format_checkbox(value)
                elif isinstance(value, str):
                    checkbox_prop = format_checkbox(value)
                elif isinstance(value, list) and value and isinstance(value[0], (bool, int, str)):
                    checkbox_prop = format_checkbox(value[0])
                else:
                    checkbox_prop = format_checkbox(False)
                
                if checkbox_prop:
                    formatted_properties[prop_name] = checkbox_prop
            
        except Exception as e:
            logger.error(f"Error formatting property {prop_name}: {e}")
    
    return formatted_properties


def create_notion_block_content(text: str, max_block_size: int = 2000) -> List[Dict[str, Any]]:
    """
    Create Notion block content from text, splitting into multiple blocks if necessary.
    
    Args:
        text: The text content
        max_block_size: Maximum characters per block
        
    Returns:
        List of Notion block objects
    """
    if not text:
        return []
    
    blocks = []
    
    # Split text into chunks of max_block_size
    for i in range(0, len(text), max_block_size):
        chunk = text[i:i + max_block_size]
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": chunk
                        }
                    }
                ]
            }
        })
    
    return blocks


def format_document_content_blocks(content: str) -> List[Dict[str, Any]]:
    """
    Format document content as Notion blocks.
    
    Args:
        content: Document content
        
    Returns:
        List of Notion blocks
    """
    return create_notion_block_content(content)


def format_document_metadata_blocks(metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Format document metadata as Notion blocks.
    
    Args:
        metadata: Document metadata
        
    Returns:
        List of Notion blocks
    """
    blocks = []
    
    # Add a heading
    blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": "Document Metadata"
                    }
                }
            ]
        }
    })
    
    # Add metadata as bulleted list
    for key, value in metadata.items():
        if value is None or value == "":
            continue
            
        if isinstance(value, (list, dict)):
            value_str = str(value)
        else:
            value_str = str(value)
            
        blocks.append({
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": f"{key}: {value_str}"
                        }
                    }
                ]
            }
        })
    
    return blocks 