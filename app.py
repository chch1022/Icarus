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
from components.input import create_portfolio_inputs, create_scenario_inputs
from components.result import create_results_section
from services.calculator import PortfolioCalculator
from services.data_manager import DataManager
from utils.validators import validate_portfolio_inputs, validate_scenario_inputs, validate_date_inputs
from utils.formatters import format_currency

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Dash app
app = dash.Dash(__name__, assets_folder='assets')
app.title = "BCI Nowcasting Tool"

# Initialize services
portfolio_calculator = PortfolioCalculator()
data_manager = DataManager()

# Set app layout
app.layout = create_main_layout()



# Callback to show input guidance when inputs change  
@app.callback(Output('portfolio-data-display', 'children'), [
    Input('group-code', 'value'),
    Input('start-date', 'date'),
    Input('end-date', 'date')
],
              prevent_initial_call=True)
def show_input_guidance(group_code: str, start_date: str, end_date: str):
    """Show input guidance without querying database."""
    # Only show guidance message, no database queries
    if not group_code or not start_date or not end_date:
        return html.Div(
            "Enter group code and dates, then click 'Run Analytics' to load portfolio data",
            style={
                'color': BCI_COLORS['gray'],
                'fontSize': '10pt',
                'fontStyle': 'italic'
            })
    else:
        return html.Div(
            "Click 'Run Analytics' to load portfolio data and calculate scenarios",
            style={
                'color': BCI_COLORS['gray'],
                'fontSize': '10pt',
                'fontStyle': 'italic'
            })


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

) -> html.Div:
    """Calculate portfolio scenarios using database data and return results."""
    logger = logging.getLogger(__name__)
    try:
        if n_clicks is None:
            return html.Div()

        # Convert date strings to date objects
        from datetime import datetime
        if not start_date or not end_date:
            return create_error_message(
                ["Start date and end date are required"])

        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()

        # Validate dates and group code
        date_validation = validate_date_inputs(group_code, start_date_obj,
                                               end_date_obj)
        if not date_validation['valid']:
            return create_error_message(date_validation['errors'])

        # Validate scenario inputs
        scenario_validation = validate_scenario_inputs(downside_rate,
                                                       base_rate, upside_rate)
        if not scenario_validation['valid']:
            return create_error_message(scenario_validation['errors'])

        # Get portfolio data from database
        beginning_mv, ending_mv = data_manager.get_market_values(
            group_code, start_date_obj, end_date_obj)
        time_horizon = data_manager.calculate_time_horizon_months(
            start_date_obj, end_date_obj)
        
        # Get real cashflows from database
        cashflows = data_manager.get_cashflows(group_code, start_date_obj, end_date_obj)

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
            cashflows=cashflows)

        # Create results display with additional context
        results_display = create_results_section(
            results, group_code, time_horizon, {
                'start_date': start_date_obj,
                'end_date': end_date_obj,
                'beginning_mv': beginning_mv,
                'ending_mv': ending_mv
            })

        logger.info(f"Successfully calculated scenarios for group: {group_code}")
        return results_display

    except Exception as e:
        logger.error(f"Error calculating scenarios: {str(e)}")
        return create_error_message([f"Calculation error: {str(e)}"])


def create_error_message(errors: List[str]) -> html.Div:
    """Create an error message display."""
    return html.Div(
        [
            html.H3("⚠️ Input Validation Errors",
                    style={
                        'color': BCI_COLORS['orange'],
                        'margin-bottom': '1rem'
                    }),
            html.Ul([
                html.Li(error,
                        style={
                            'color': BCI_COLORS['text_black'],
                            'margin-bottom': '0.5rem'
                        }) for error in errors
            ])
        ],
        style={
            'padding': '1.5rem',
            'border': f'2px solid {BCI_COLORS["orange"]}',
            'border-radius': '8px',
            'background-color': '#fff5f5',
            'margin': '1rem 0'
        })


if __name__ == '__main__':
    logger.info("Starting BCI Nowcasting Tool")
    app.run(host=APP_CONFIG['host'],
            port=APP_CONFIG['port'],
            debug=APP_CONFIG['debug'])
