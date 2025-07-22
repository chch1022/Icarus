"""
Formatting utilities for BCI Nowcasting Tool.

Provides functions for formatting currency, numbers, and other display values.
"""

from typing import Union
from config.setting import CURRENCY_CONFIG

def format_currency(value: Union[float, int]) -> str:
    """
    Format a numeric value as currency.
    
    Args:
        value: Numeric value to format
        
    Returns:
        Formatted currency string
    """
    if value is None:
        return "N/A"
    
    symbol = CURRENCY_CONFIG['symbol']
    decimal_places = CURRENCY_CONFIG['decimal_places']
    separator = CURRENCY_CONFIG['thousands_separator']
    
    # Handle negative values
    is_negative = value < 0
    abs_value = abs(value)
    
    # Format with appropriate decimal places
    if decimal_places == 0:
        formatted_value = f"{abs_value:,.0f}"
    else:
        formatted_value = f"{abs_value:,.{decimal_places}f}"
    
    # Replace comma separator if different
    if separator != ',':
        formatted_value = formatted_value.replace(',', separator)
    
    # Add currency symbol and handle negative sign
    if is_negative:
        return f"-{symbol}{formatted_value}"
    else:
        return f"{symbol}{formatted_value}"

def format_percentage(value: Union[float, int], decimal_places: int = 1) -> str:
    """
    Format a numeric value as percentage.
    
    Args:
        value: Numeric value to format
        decimal_places: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    if value is None:
        return "N/A"
    
    return f"{value:+.{decimal_places}f}%"

def format_number(value: Union[float, int], decimal_places: int = 0) -> str:
    """
    Format a numeric value with thousands separator.
    
    Args:
        value: Numeric value to format
        decimal_places: Number of decimal places
        
    Returns:
        Formatted number string
    """
    if value is None:
        return "N/A"
    
    if decimal_places == 0:
        return f"{value:,.0f}"
    else:
        return f"{value:,.{decimal_places}f}"

def format_month_year(month: int) -> str:
    """
    Format month number as descriptive text.
    
    Args:
        month: Month number (1-120)
        
    Returns:
        Formatted month description
    """
    if month <= 0:
        return "Invalid month"
    
    years = (month - 1) // 12
    months = (month - 1) % 12 + 1
    
    if years == 0:
        return f"Month {months}"
    elif years == 1:
        return f"Year 1, Month {months}"
    else:
        return f"Year {years + 1}, Month {months}"
