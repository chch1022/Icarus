"""
Configuration settings for BCI Nowcasting Tool.

Contains color palette, styling constants, and application configuration.
"""

import os
from typing import Dict, Any

# BCI Color Palette
BCI_COLORS: Dict[str, str] = {
    'midnight': '#00365b',
    'ocean': '#00abbd',
    'gray': '#696f79',
    'slate': '#457b96',
    'khaki': '#a6b38c',
    'purple': '#4a317e',
    'yellow': '#fdb736',
    'orange': '#dc642b',
    'emerald': '#819f4d',
    'jade': '#57837b',
    'amethyst': '#864c9e',
    'garnet': '#ae1e57',
    'melon': '#f68e47',
    'pear': '#c1b64e',
    'dark_ocean': '#0091a1',
    'text_black': '#48484A',
    'gray_1': '#F2F2F2',
    'gray_2': '#D9D9D9',
    'gray_3': '#BFBFBF'
}

# Scenario Configuration
SCENARIO_CONFIG: Dict[str, Dict[str, Any]] = {
    'downside': {
        'color': BCI_COLORS['orange'],
        'icon': '🔻',
        'label': 'Downside Scenario',
        'css_class': 'scenario-downside'
    },
    'base': {
        'color': BCI_COLORS['ocean'],
        'icon': '➖',
        'label': 'Base Scenario',
        'css_class': 'scenario-base'
    },
    'upside': {
        'color': BCI_COLORS['emerald'],
        'icon': '📈',
        'label': 'Upside Scenario',
        'css_class': 'scenario-upside'
    }
}

# Input Styling
INPUT_STYLE: Dict[str, str] = {
    'width': '100%',
    'padding': '0.75rem',
    'border': f'1px solid {BCI_COLORS["gray_3"]}',
    'borderRadius': '4px',
    'fontSize': '11pt'
}

# Button Styling
BUTTON_STYLES: Dict[str, Dict[str, str]] = {
    'primary': {
        'backgroundColor': BCI_COLORS['midnight'],
        'color': 'white',
        'border': 'none',
        'padding': '1rem 2rem',
        'borderRadius': '4px',
        'fontSize': '11pt',
        'fontWeight': 'bold',
        'cursor': 'pointer'
    },
    'secondary': {
        'backgroundColor': BCI_COLORS['ocean'],
        'color': 'white',
        'border': 'none',
        'padding': '0.5rem 1rem',
        'borderRadius': '4px',
        'cursor': 'pointer'
    }
}

# Application Configuration
APP_CONFIG: Dict[str, Any] = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': os.getenv('DEBUG', 'False').lower() == 'true',
    'max_cashflows': 10,
    'default_time_horizon': 12,
    'min_time_horizon': 1,
    'max_time_horizon': 120
}

# Validation Rules
VALIDATION_RULES: Dict[str, Dict[str, Any]] = {
    'beginning_mv': {
        'min': 1000,
        'max': 1000000000,
        'required': True
    },
    'time_horizon': {
        'min': APP_CONFIG['min_time_horizon'],
        'max': APP_CONFIG['max_time_horizon'],
        'required': True
    },
    'rates': {
        'min': -50,
        'max': 100,
        'required': True
    },
    'cashflow_amount': {
        'min': -1000000000,
        'max': 1000000000,
        'required': False
    }
}

# Application Configuration
APP_CONFIG: Dict[str, Any] = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': os.getenv('DEBUG', 'False').lower() == 'true',
    'max_cashflows': 10,
    'default_time_horizon': 12,
    'min_time_horizon': 1,
    'max_time_horizon': 120
}

# Currency Formatting
CURRENCY_CONFIG: Dict[str, Any] = {
    'symbol': '$',
    'decimal_places': 0,
    'thousands_separator': ','
}

# Methodology Text
METHODOLOGY_TEXT: str = """
Methodology: Future values are calculated using compound interest formulas. 
Portfolio value grows at the specified annual return rate, compounded monthly. 
Cashflows are projected to the end of the time horizon using the same rate assumptions. 
All calculations assume constant return rates throughout the forecast period.
Results are for illustrative purposes only and do not constitute investment advice.
"""
