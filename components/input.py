"""
Input form components for BCI Nowcasting Tool.

Provides reusable form components for portfolio details, scenarios, and cashflows.
"""

from dash import html, dcc
from config.setting import BCI_COLORS, SCENARIO_CONFIG, INPUT_STYLE


def create_portfolio_inputs() -> html.Div:
    """
    Create portfolio details input form with database integration.
    
    Returns:
        Dash HTML component with portfolio input fields
    """
    from datetime import date, timedelta
    
    # Default dates - last month as example
    today = date.today()
    default_end_date = date(today.year, today.month, 1) - timedelta(days=1)  # Last day of previous month
    default_start_date = date(default_end_date.year, default_end_date.month, 1)  # First day of previous month
    
    return html.Div([
        html.H2("Portfolio Details", className="section-header"),
        
        html.Div([
            html.Label("Group Code", className="input-label"),
            dcc.Input(
                id='group-code',
                type='text',
                placeholder='Enter group code',
                style=INPUT_STYLE
            )
        ], className="input-group"),
        
        html.Div([
            html.Label("Period Start Date", className="input-label"),
            dcc.DatePickerSingle(
                id='start-date',
                date=default_start_date,
                display_format='YYYY-MM-DD',
                style={'width': '100%'}
            )
        ], className="input-group"),
        
        html.Div([
            html.Label("Period End Date", className="input-label"),
            dcc.DatePickerSingle(
                id='end-date',
                date=default_end_date,
                display_format='YYYY-MM-DD',
                style={'width': '100%'}
            )
        ], className="input-group"),
        
        # Display calculated values from database
        html.Div(id='portfolio-data-display', children=[
            html.Div("Enter group code and dates to load portfolio data", 
                    style={'color': BCI_COLORS['gray'], 'fontSize': '10pt', 'fontStyle': 'italic'})
        ], style={'margin': '1rem 0', 'padding': '1rem', 'backgroundColor': BCI_COLORS['gray_1'], 'borderRadius': '4px'}),
    ])

def create_scenario_inputs() -> html.Div:
    """
    Create return scenarios input form.
    
    Returns:
        Dash HTML component with scenario input fields
    """
    return html.Div([
        html.H2("Return Scenarios (%)", className="section-header"),
        
        html.Div([
            html.Label(
                f"{SCENARIO_CONFIG['downside']['icon']} {SCENARIO_CONFIG['downside']['label']}", 
                className="input-label",
                style={'color': SCENARIO_CONFIG['downside']['color']}
            ),
            dcc.Input(
                id='downside-rate',
                type='number',
                value=-5,
                step=0.1,
                style=INPUT_STYLE
            )
        ], className="input-group"),
        
        html.Div([
            html.Label(
                f"{SCENARIO_CONFIG['base']['icon']} {SCENARIO_CONFIG['base']['label']}", 
                className="input-label",
                style={'color': SCENARIO_CONFIG['base']['color']}
            ),
            dcc.Input(
                id='base-rate',
                type='number',
                value=7,
                step=0.1,
                style=INPUT_STYLE
            )
        ], className="input-group"),
        
        html.Div([
            html.Label(
                f"{SCENARIO_CONFIG['upside']['icon']} {SCENARIO_CONFIG['upside']['label']}", 
                className="input-label",
                style={'color': SCENARIO_CONFIG['upside']['color']}
            ),
            dcc.Input(
                id='upside-rate',
                type='number',
                value=15,
                step=0.1,
                style=INPUT_STYLE
            )
        ], className="input-group"),
    ])


