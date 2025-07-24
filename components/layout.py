"""
Main layout components for BCI Nowcasting Tool.

Provides the overall application structure and styling.
"""

from dash import html
from config.setting import BCI_COLORS

def create_main_layout() -> html.Div:
    """
    Create the main application layout with enhanced design.
    
    Returns:
        Dash HTML component with the complete app layout
    """
    return html.Div([
        # Enhanced Header
        html.Div([
            html.Div([
                # Header left side
                html.Div([
                    html.Div([
                        html.Img(src="/assets/bci-logo.svg", className="bci-logo"),
                    ], className="logo-container"),

                ], className="header-left"),
            ], className="header-content")
        ], className="header"),
        
        # Content
        html.Div([
            # Input Section
            html.Div([
                create_input_section()
            ]),
            
            # Calculate Button
            html.Div([
                html.Button(
                    "Run Analytics",
                    id='calculate-btn',
                    className="calculate-button"
                )
            ], className="button-container"),
            
            # Results Section
            html.Div(id='results-section')
            
        ], className="content")
        
    ], className="main-container")

def create_input_section() -> html.Div:
    """
    Create the input section with modern card-based layout.
    
    Returns:
        Dash HTML component with input forms
    """
    from components.input import create_portfolio_inputs, create_scenario_inputs
    
    return html.Div([
        # Portfolio Details Card
        html.Div([
            create_portfolio_inputs()
        ], className="input-card"),
        
        # Return Scenarios Card
        html.Div([
            create_scenario_inputs()
        ], className="input-card")
    ], className="input-grid")
