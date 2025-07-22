"""
Main layout components for BCI Nowcasting Tool.

Provides the overall application structure and styling.
"""

from dash import html
from config.setting import BCI_COLORS

def create_main_layout() -> html.Div:
    """
    Create the main application layout.
    
    Returns:
        Dash HTML component with the complete app layout
    """
    return html.Div([
        # Header
        html.Div([
            html.H1("BCI Nowcasting Tool"),
            html.P("Scenario-based portfolio valuation forecasting")
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
                    "🧮 Run Nowcast Analysis",
                    id='calculate-btn',
                    style={
                        'backgroundColor': BCI_COLORS['midnight'],
                        'color': 'white',
                        'border': 'none',
                        'padding': '1rem 2rem',
                        'borderRadius': '4px',
                        'fontSize': '11pt',
                        'fontWeight': 'bold',
                        'cursor': 'pointer',
                        'display': 'block',
                        'margin': '2rem auto'
                    }
                )
            ], style={'textAlign': 'center'}),
            
            # Results Section
            html.Div(id='results-section')
            
        ], className="content")
        
    ], className="main-container")

def create_input_section() -> html.Div:
    """
    Create the input section with portfolio details and scenarios.
    
    Returns:
        Dash HTML component with input forms
    """
    from components.input import create_portfolio_inputs, create_scenario_inputs, create_cashflow_section
    
    return html.Div([
        html.Div([
            # Portfolio Details
            create_portfolio_inputs()
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        html.Div([
            # Return Scenarios
            create_scenario_inputs()
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginLeft': '4%'}),
        
        # Cashflows Section (full width)
        html.Div([
            create_cashflow_section()
        ], style={'clear': 'both', 'marginTop': '2rem'})
    ])
