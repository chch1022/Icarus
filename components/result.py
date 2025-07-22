"""
Results display components for BCI Nowcasting Tool.

Provides components for displaying calculation results and scenario analysis.
"""

from dash import html
from typing import Dict, Optional, Any
from datetime import datetime, date

from config.setting import BCI_COLORS, SCENARIO_CONFIG, METHODOLOGY_TEXT
from services.calculator import ScenarioResult, CashflowFVItem
from utils.formatters import format_currency

def create_results_section(
    results: Dict[str, ScenarioResult], 
    group_code: Optional[str], 
    time_horizon: int,
    context: Optional[Dict[str, Any]] = None
) -> html.Div:
    """
    Create the results display section.
    
    Args:
        results: Dictionary of scenario results
        group_code: Portfolio group code
        time_horizon: Forecast time horizon in months
        
    Returns:
        Dash HTML component with formatted results
    """
    if not results:
        return html.Div([
            html.H3("No results to display", style={'color': BCI_COLORS['text_black']})
        ])
    
    # Use context dates if provided, otherwise calculate
    if context and 'start_date' in context and 'end_date' in context:
        start_date = context['start_date']
        end_date = context['end_date'] 
        ending_mv = context.get('ending_mv', 0)
    else:
        # Fallback to current date calculation
        start_date = datetime.now().date()
        end_date = datetime.now()
        for _ in range(time_horizon):
            if end_date.month == 12:
                end_date = end_date.replace(year=end_date.year + 1, month=1)
            else:
                end_date = end_date.replace(month=end_date.month + 1)
        end_date = end_date.date()
        ending_mv = None
    
    return html.Div([
        # Results Header
        html.H2("Nowcast Analysis Results", className="section-header"),
        
        # Portfolio Summary
        create_portfolio_summary(group_code, time_horizon, start_date, end_date, ending_mv),
        
        # Scenario Cards
        html.Div([
            create_scenario_card(results.get('downside'), 'downside'),
            create_scenario_card(results.get('base'), 'base'),
            create_scenario_card(results.get('upside'), 'upside')
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '1rem', 'margin': '1rem 0'}),
        
        # Detailed Cashflow Analysis (if cashflows exist)
        create_cashflow_analysis_section(results, context or {}),
        
        # Methodology
        create_methodology_section()
    ])

def create_portfolio_summary(
    group_code: Optional[str], 
    time_horizon: int, 
    start_date: date,
    end_date: date,
    ending_mv: Optional[float] = None
) -> html.Div:
    """
    Create portfolio summary information.
    
    Args:
        group_code: Portfolio group code
        time_horizon: Forecast time horizon
        end_date: Forecast end date
        
    Returns:
        Dash HTML component with portfolio summary
    """
    summary_items = [
        html.P([
            html.Strong("Group Code: "), 
            group_code or "Not specified"
        ], style={'margin': '0.5rem 0', 'fontSize': '11pt'}),
        
        html.P([
            html.Strong("Analysis Period: "), 
            f"{start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')} ({time_horizon} months)"
        ], style={'margin': '0.5rem 0', 'fontSize': '11pt'}),
        
        html.P([
            html.Strong("Analysis Date: "), 
            datetime.now().strftime("%B %d, %Y")
        ], style={'margin': '0.5rem 0', 'fontSize': '11pt'}),
    ]
    
    # Add actual ending market value if available
    if ending_mv is not None:
        summary_items.append(
            html.P([
                html.Strong("Actual Ending Market Value: "), 
                format_currency(ending_mv),
                html.Span(" (from database)", style={'fontSize': '9pt', 'color': BCI_COLORS['gray']})
            ], style={'margin': '0.5rem 0', 'fontSize': '11pt'})
        )
    
    return html.Div(summary_items, style={
        'backgroundColor': BCI_COLORS['gray_1'],
        'padding': '1rem',
        'borderRadius': '4px',
        'margin': '1rem 0'
    })

def create_scenario_card(result: Optional[ScenarioResult], scenario_type: str) -> html.Div:
    """
    Create a single scenario result card.
    
    Args:
        result: Scenario calculation result
        scenario_type: Type of scenario (downside, base, upside)
        
    Returns:
        Dash HTML component with scenario card
    """
    if not result:
        return html.Div()
    
    config = SCENARIO_CONFIG[scenario_type]
    
    return html.Div([
        # Scenario Title
        html.Div([
            f"{config['icon']} {config['label']} ({result.rate:+.1f}%)"
        ], className="scenario-title"),
        
        # Portfolio Future Value
        html.Div([
            html.Strong("Portfolio Future Value: "),
            format_currency(result.portfolio_fv)
        ], style={'margin': '0.5rem 0', 'fontSize': '10pt'}),
        
        # Cashflow Future Value
        html.Div([
            html.Strong("Cashflows Future Value: "),
            format_currency(result.cashflow_fv)
        ], style={'margin': '0.5rem 0', 'fontSize': '10pt'}),
        
        # Total Future Value
        html.Div([
            html.Strong("Total Future Value: "),
            format_currency(result.total_fv)
        ], className="total-fv"),
        
    ], className=f"scenario-card {config['css_class']}", style={'flex': '1', 'minWidth': '300px'})

def create_cashflow_analysis_section(results: Dict[str, ScenarioResult], context: Optional[dict] = None) -> html.Div:
    """
    Create comprehensive forecast table showing both market values and cashflows with scenario forecasts.
    
    Args:
        results: Dictionary of scenario results
        
    Returns:
        Dash HTML component with comprehensive forecast table
    """
    base_result = results.get('base')
    if not base_result:
        return html.Div()
    
    downside_result = results.get('downside')
    upside_result = results.get('upside')
    
    # Create table header
    table_header = html.Tr([
        html.Th("Date", style={'padding': '0.5rem', 'textAlign': 'left', 'borderBottom': f'2px solid {BCI_COLORS["gray"]}', 'fontSize': '10pt', 'fontWeight': 'bold'}),
        html.Th("Type", style={'padding': '0.5rem', 'textAlign': 'center', 'borderBottom': f'2px solid {BCI_COLORS["gray"]}', 'fontSize': '10pt', 'fontWeight': 'bold'}),
        html.Th("Amount", style={'padding': '0.5rem', 'textAlign': 'right', 'borderBottom': f'2px solid {BCI_COLORS["gray"]}', 'fontSize': '10pt', 'fontWeight': 'bold'}),
        html.Th("Downside Forecast", style={'padding': '0.5rem', 'textAlign': 'right', 'borderBottom': f'2px solid {BCI_COLORS["gray"]}', 'fontSize': '10pt', 'fontWeight': 'bold', 'color': SCENARIO_CONFIG['downside']['color']}),
        html.Th("Base Forecast", style={'padding': '0.5rem', 'textAlign': 'right', 'borderBottom': f'2px solid {BCI_COLORS["gray"]}', 'fontSize': '10pt', 'fontWeight': 'bold', 'color': SCENARIO_CONFIG['base']['color']}),
        html.Th("Upside Forecast", style={'padding': '0.5rem', 'textAlign': 'right', 'borderBottom': f'2px solid {BCI_COLORS["gray"]}', 'fontSize': '10pt', 'fontWeight': 'bold', 'color': SCENARIO_CONFIG['upside']['color']}),
    ])
    
    table_rows = [table_header]
    
    # Get Beginning Market Value from context or calculate it back
    if context and 'beginning_mv' in context:
        beginning_mv = context['beginning_mv']
        start_date = context.get('start_date', 'Beginning')
        start_date_str = start_date.strftime('%m/%d/%Y') if hasattr(start_date, 'strftime') else 'Beginning'
    else:
        # Back-calculate BMV from portfolio FV and rate (fallback)
        beginning_mv = base_result.portfolio_fv / (1 + base_result.rate/100)**1  # Simplified back-calc
        start_date_str = "Beginning"
    
    # Add Beginning Market Value row (this grows to portfolio FV)
    bmv_row = html.Tr([
        html.Td(start_date_str, style={'padding': '0.5rem', 'fontSize': '9pt'}),
        html.Td("MV", style={'padding': '0.5rem', 'textAlign': 'center', 'fontSize': '9pt', 'fontWeight': 'bold'}),
        html.Td(format_currency(beginning_mv), style={'padding': '0.5rem', 'textAlign': 'right', 'fontSize': '9pt'}),
        html.Td(format_currency(downside_result.portfolio_fv if downside_result else 0), style={'padding': '0.5rem', 'textAlign': 'right', 'fontSize': '9pt', 'color': SCENARIO_CONFIG['downside']['color']}),
        html.Td(format_currency(base_result.portfolio_fv), style={'padding': '0.5rem', 'textAlign': 'right', 'fontSize': '9pt', 'color': SCENARIO_CONFIG['base']['color']}),
        html.Td(format_currency(upside_result.portfolio_fv if upside_result else 0), style={'padding': '0.5rem', 'textAlign': 'right', 'fontSize': '9pt', 'color': SCENARIO_CONFIG['upside']['color']}),
    ])
    table_rows.append(bmv_row)
    
    # Add cashflow rows if they exist
    if base_result.cashflow_details:
        for cf in base_result.cashflow_details:
            cf_row = html.Tr([
                html.Td(f"Month {cf.month}", style={'padding': '0.5rem', 'fontSize': '9pt'}),
                html.Td("CF", style={'padding': '0.5rem', 'textAlign': 'center', 'fontSize': '9pt', 'fontWeight': 'bold'}),
                html.Td(format_currency(cf.amount), style={'padding': '0.5rem', 'textAlign': 'right', 'fontSize': '9pt'}),
                html.Td(format_currency(cf.fv_downside), style={'padding': '0.5rem', 'textAlign': 'right', 'fontSize': '9pt', 'color': SCENARIO_CONFIG['downside']['color']}),
                html.Td(format_currency(cf.fv_base), style={'padding': '0.5rem', 'textAlign': 'right', 'fontSize': '9pt', 'color': SCENARIO_CONFIG['base']['color']}),
                html.Td(format_currency(cf.fv_upside), style={'padding': '0.5rem', 'textAlign': 'right', 'fontSize': '9pt', 'color': SCENARIO_CONFIG['upside']['color']}),
            ])
            table_rows.append(cf_row)
    
    # Add separator line before total
    separator_row = html.Tr([
        html.Td("", colSpan=6, style={'borderTop': f'2px solid {BCI_COLORS["gray"]}', 'padding': '0.25rem'})
    ])
    table_rows.append(separator_row)
    
    # Add total forecast row
    total_row = html.Tr([
        html.Td(html.Strong("TOTAL"), style={'padding': '0.75rem', 'fontSize': '11pt', 'fontWeight': 'bold'}),
        html.Td(html.Strong("FORECAST"), style={'padding': '0.75rem', 'textAlign': 'center', 'fontSize': '11pt', 'fontWeight': 'bold'}),
        html.Td("", style={'padding': '0.75rem'}),  # No original amount for total
        html.Td(html.Strong(format_currency(downside_result.total_fv if downside_result else 0)), 
                style={'padding': '0.75rem', 'textAlign': 'right', 'fontSize': '11pt', 'fontWeight': 'bold', 'color': SCENARIO_CONFIG['downside']['color'], 'backgroundColor': f'{SCENARIO_CONFIG["downside"]["color"]}15'}),
        html.Td(html.Strong(format_currency(base_result.total_fv)), 
                style={'padding': '0.75rem', 'textAlign': 'right', 'fontSize': '11pt', 'fontWeight': 'bold', 'color': SCENARIO_CONFIG['base']['color'], 'backgroundColor': f'{SCENARIO_CONFIG["base"]["color"]}15'}),
        html.Td(html.Strong(format_currency(upside_result.total_fv if upside_result else 0)), 
                style={'padding': '0.75rem', 'textAlign': 'right', 'fontSize': '11pt', 'fontWeight': 'bold', 'color': SCENARIO_CONFIG['upside']['color'], 'backgroundColor': f'{SCENARIO_CONFIG["upside"]["color"]}15'}),
    ])
    table_rows.append(total_row)
    
    return html.Div([
        html.H3("Portfolio Forecast Analysis", style={
            'color': BCI_COLORS['text_black'],
            'fontSize': '12pt',
            'fontWeight': 'bold',
            'margin': '1.5rem 0 0.5rem 0'
        }),
        html.Table(
            table_rows,
            style={
                'width': '100%',
                'backgroundColor': '#ffffff',
                'border': f'1px solid {BCI_COLORS["gray"]}',
                'borderRadius': '4px',
                'overflow': 'hidden',
                'margin': '0.5rem 0'
            }
        )
    ])

def create_methodology_section() -> html.Div:
    """
    Create methodology explanation section.
    
    Returns:
        Dash HTML component with methodology text
    """
    return html.Div([
        html.H3("Methodology", style={
            'color': BCI_COLORS['text_black'],
            'fontSize': '10pt',
            'fontWeight': 'bold',
            'marginBottom': '0.5rem'
        }),
        html.P(METHODOLOGY_TEXT, style={
            'fontSize': '8pt',
            'color': BCI_COLORS['text_black'],
            'lineHeight': '1.4',
            'margin': '0'
        })
    ], className="methodology")
