"""
BCI Nowcasting Tool - Main Application Entry Point

A Dash-based portfolio forecasting application with scenario analysis.
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context
import logging
from typing import Dict, Any, List, Optional

from config.setting import APP_CONFIG, BCI_COLORS
from components.layout import create_main_layout
from components.input import create_portfolio_inputs, create_scenario_inputs, create_cashflow_section
from components.result import create_results_section
from services.calculator import PortfolioCalculator
from services.data_manager import DataManager
from utils.validators import validate_portfolio_inputs, validate_scenario_inputs, validate_date_inputs
from utils.formatters import format_currency

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Dash app
app = dash.Dash(__name__, assets_folder='assets')
app.title = "BCI Nowcasting Tool"

# Initialize services
portfolio_calculator = PortfolioCalculator()
data_manager = DataManager()

# Set app layout
app.layout = create_main_layout()

@app.callback(
    Output('cashflow-container', 'children'),
    Input('add-cashflow-btn', 'n_clicks'),
    State('cashflow-container', 'children'),
    prevent_initial_call=False
)
def add_cashflow_row(n_clicks: Optional[int], existing_children: List[Dict]) -> List[Dict]:
    """Add a new cashflow input row to the form."""
    try:
        if existing_children is None:
            existing_children = []
        
        if n_clicks is None:
            n_clicks = 0
        
        # Add new cashflow row
        new_row = cashflow_manager.create_cashflow_row(len(existing_children))
        existing_children.append(new_row)
        
        logger.info(f"Added cashflow row. Total rows: {len(existing_children)}")
        return existing_children
        
    except Exception as e:
        logger.error(f"Error adding cashflow row: {str(e)}")
        return existing_children or []

# Callback to load portfolio data when inputs change
@app.callback(
    Output('portfolio-data-display', 'children'),
    [
        Input('group-code', 'value'),
        Input('start-date', 'date'),
        Input('end-date', 'date')
    ],
    prevent_initial_call=True
)
def load_portfolio_data(group_code: str, start_date: str, end_date: str):
    """Load and display portfolio data from database."""
    try:
        if not group_code or not start_date or not end_date:
            return html.Div("Enter group code and dates to load portfolio data", 
                          style={'color': BCI_COLORS['gray'], 'fontSize': '10pt', 'fontStyle': 'italic'})
        
        # Convert date strings to date objects
        from datetime import datetime
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Validate dates
        date_validation = validate_date_inputs(group_code, start_date_obj, end_date_obj)
        if not date_validation['valid']:
            return create_error_message(date_validation['errors'])
        
        # Get portfolio data from database
        beginning_mv, ending_mv = data_manager.get_market_values(group_code, start_date_obj, end_date_obj)
        cashflows = data_manager.get_cashflows(group_code, start_date_obj, end_date_obj)
        time_horizon = data_manager.calculate_time_horizon_months(start_date_obj, end_date_obj)
        
        # Display the loaded data
        return html.Div([
            html.Div([
                html.Strong("Beginning Market Value: "),
                format_currency(beginning_mv)
            ], style={'margin': '0.5rem 0'}),
            html.Div([
                html.Strong("Ending Market Value: "),
                format_currency(ending_mv)
            ], style={'margin': '0.5rem 0'}),
            html.Div([
                html.Strong("Time Horizon: "),
                f"{time_horizon} months"
            ], style={'margin': '0.5rem 0'}),
            html.Div([
                html.Strong("Historical Cashflows: "),
                f"{len(cashflows)} transactions found"
            ], style={'margin': '0.5rem 0'}),
        ], style={'color': BCI_COLORS['text_black']})
        
    except Exception as e:
        logger.error(f"Error loading portfolio data: {str(e)}")
        return html.Div(f"Error loading data: {str(e)}", 
                      style={'color': BCI_COLORS['orange'], 'fontSize': '10pt'})

@app.callback(
    Output('results-section', 'children'),
    Input('calculate-btn', 'n_clicks'),
    [
        State('group-code', 'value'),
        State('start-date', 'date'),
        State('end-date', 'date'),
        State('downside-rate', 'value'),
        State('base-rate', 'value'),
        State('upside-rate', 'value'),
        State('cashflow-container', 'children')
    ],
    prevent_initial_call=True
)
def calculate_scenarios(
    n_clicks: Optional[int],
    group_code: Optional[str],
    start_date: Optional[str],
    end_date: Optional[str],
    downside_rate: Optional[float],
    base_rate: Optional[float],
    upside_rate: Optional[float],
    cashflow_children: Optional[List[Dict]]
) -> Dict[str, Any]:
    """Calculate portfolio scenarios using database data and return results."""
    try:
        if n_clicks is None:
            return html.Div()
        
        # Convert date strings to date objects
        from datetime import datetime
        if not start_date or not end_date:
            return create_error_message(["Start date and end date are required"])
        
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Validate dates and group code
        date_validation = validate_date_inputs(group_code, start_date_obj, end_date_obj)
        if not date_validation['valid']:
            return create_error_message(date_validation['errors'])
        
        # Validate scenario inputs
        scenario_validation = validate_scenario_inputs(
            downside_rate, base_rate, upside_rate
        )
        if not scenario_validation['valid']:
            return create_error_message(scenario_validation['errors'])
        
        # Get portfolio data from database
        beginning_mv, ending_mv = data_manager.get_market_values(group_code, start_date_obj, end_date_obj)
        time_horizon = data_manager.calculate_time_horizon_months(start_date_obj, end_date_obj)
        
        # Extract additional cashflows from form (future projections)
        additional_cashflows = cashflow_manager.extract_cashflows_from_form(cashflow_children or [])
        
        # Add demo cashflows if none exist to demonstrate the table functionality
        if not additional_cashflows and group_code == 'PROG-001':
            from services.portfolio_calculator import CashflowItem
            additional_cashflows = [
                CashflowItem(amount=50000.0, month=3, description="Q1 Dividend Payment"),
                CashflowItem(amount=-15000.0, month=6, description="Management Fee"),
                CashflowItem(amount=75000.0, month=9, description="Capital Contribution"),
                CashflowItem(amount=25000.0, month=12, description="Q4 Bonus Distribution")
            ]
        
        # Calculate scenarios
        scenarios = {
            'downside': downside_rate,
            'base': base_rate,
            'upside': upside_rate
        }
        
        results = portfolio_calculator.calculate_all_scenarios(
            beginning_mv=beginning_mv,
            time_horizon=time_horizon,
            scenarios=scenarios,
            cashflows=additional_cashflows
        )
        
        # Create results display with additional context
        results_display = create_results_section(
            results, 
            group_code, 
            time_horizon,
            {
                'start_date': start_date_obj,
                'end_date': end_date_obj,
                'beginning_mv': beginning_mv,
                'ending_mv': ending_mv
            }
        )
        
        logger.info(f"Successfully calculated scenarios for group: {group_code}")
        return results_display
        
    except Exception as e:
        logger.error(f"Error calculating scenarios: {str(e)}")
        return create_error_message([f"Calculation error: {str(e)}"])

def create_error_message(errors: List[str]) -> html.Div:
    """Create an error message display."""
    return html.Div([
        html.H3("⚠️ Input Validation Errors", 
               style={'color': BCI_COLORS['orange'], 'margin-bottom': '1rem'}),
        html.Ul([
            html.Li(error, style={'color': BCI_COLORS['text_black'], 'margin-bottom': '0.5rem'})
            for error in errors
        ])
    ], style={
        'padding': '1.5rem',
        'border': f'2px solid {BCI_COLORS["orange"]}',
        'border-radius': '8px',
        'background-color': '#fff5f5',
        'margin': '1rem 0'
    })

if __name__ == '__main__':
    logger.info("Starting BCI Nowcasting Tool")
    app.run(
        host=APP_CONFIG['host'],
        port=APP_CONFIG['port'],
        debug=APP_CONFIG['debug']
    )
