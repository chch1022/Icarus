"""
Input validation utilities for BCI Nowcasting Tool.

Provides validation functions for user inputs and data integrity checks.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import date, timedelta

from config.setting import VALIDATION_RULES, APP_CONFIG

logger = logging.getLogger(__name__)

def validate_portfolio_inputs(
    group_code: Optional[str],
    beginning_mv: Optional[Union[float, int]],
    time_horizon: Optional[Union[int, float]]
) -> Dict[str, Any]:
    """
    Validate portfolio input parameters.
    
    Args:
        group_code: Portfolio group identifier
        beginning_mv: Beginning market value
        time_horizon: Forecast time horizon in months
        
    Returns:
        Dictionary with validation results and error messages
    """
    errors = []
    
    # Validate group code
    if not group_code or not group_code.strip():
        errors.append("Group code is required")
    elif len(group_code.strip()) > 50:
        errors.append("Group code must be 50 characters or less")
    
    # Validate beginning market value
    if beginning_mv is None:
        errors.append("Beginning market value is required")
    else:
        mv_rules = VALIDATION_RULES['beginning_mv']
        if beginning_mv < mv_rules['min']:
            errors.append(f"Beginning market value must be at least ${mv_rules['min']:,}")
        elif beginning_mv > mv_rules['max']:
            errors.append(f"Beginning market value must be less than ${mv_rules['max']:,}")
    
    # Validate time horizon
    if time_horizon is None:
        errors.append("Time horizon is required")
    else:
        horizon_rules = VALIDATION_RULES['time_horizon']
        if not isinstance(time_horizon, int) or time_horizon != int(time_horizon):
            errors.append("Time horizon must be a whole number")
        elif time_horizon < horizon_rules['min']:
            errors.append(f"Time horizon must be at least {horizon_rules['min']} month(s)")
        elif time_horizon > horizon_rules['max']:
            errors.append(f"Time horizon must be no more than {horizon_rules['max']} months")
    
    result = {
        'valid': len(errors) == 0,
        'errors': errors
    }
    
    if errors:
        logger.warning(f"Portfolio input validation failed: {errors}")
    
    return result

def validate_scenario_inputs(
    downside_rate: Optional[Union[float, int]],
    base_rate: Optional[Union[float, int]],
    upside_rate: Optional[Union[float, int]]
) -> Dict[str, Any]:
    """
    Validate return scenario input parameters.
    
    Args:
        downside_rate: Downside scenario return rate
        base_rate: Base scenario return rate
        upside_rate: Upside scenario return rate
        
    Returns:
        Dictionary with validation results and error messages
    """
    errors = []
    rate_rules = VALIDATION_RULES['rates']
    
    # Validate individual rates
    rates = {
        'Downside': downside_rate,
        'Base': base_rate,
        'Upside': upside_rate
    }
    
    valid_rates = {}
    
    for scenario_name, rate in rates.items():
        if rate is None:
            errors.append(f"{scenario_name} scenario rate is required")
        else:
            if rate < rate_rules['min']:
                errors.append(f"{scenario_name} rate must be at least {rate_rules['min']}%")
            elif rate > rate_rules['max']:
                errors.append(f"{scenario_name} rate must be no more than {rate_rules['max']}%")
            else:
                valid_rates[scenario_name] = rate
    
    # Validate rate relationships (if all rates are valid)
    if len(valid_rates) == 3:
        if valid_rates['Downside'] >= valid_rates['Base']:
            errors.append("Downside rate should be lower than base rate")
        
        if valid_rates['Base'] >= valid_rates['Upside']:
            errors.append("Base rate should be lower than upside rate")
        
        if valid_rates['Downside'] >= valid_rates['Upside']:
            errors.append("Downside rate should be lower than upside rate")
    
    result = {
        'valid': len(errors) == 0,
        'errors': errors
    }
    
    if errors:
        logger.warning(f"Scenario input validation failed: {errors}")
    
    return result

def validate_cashflow_inputs(
    amount: Optional[Union[float, int]],
    month: Optional[Union[int, float]],
    description: Optional[str]
) -> Dict[str, Any]:
    """
    Validate cashflow input parameters.
    
    Args:
        amount: Cashflow amount
        month: Month when cashflow occurs
        description: Cashflow description
        
    Returns:
        Dictionary with validation results and error messages
    """
    errors = []
    
    # Validate amount
    if amount is None:
        errors.append("Cashflow amount is required")
    else:
        amount_rules = VALIDATION_RULES['cashflow_amount']
        if amount < amount_rules['min']:
            errors.append(f"Cashflow amount must be at least ${amount_rules['min']:,}")
        elif amount > amount_rules['max']:
            errors.append(f"Cashflow amount must be no more than ${amount_rules['max']:,}")
    
    # Validate month
    if month is None:
        errors.append("Cashflow month is required")
    else:
        if not isinstance(month, int) or month != int(month):
            errors.append("Cashflow month must be a whole number")
        elif month < 1:
            errors.append("Cashflow month must be at least 1")
        elif month > APP_CONFIG['max_time_horizon']:
            errors.append(f"Cashflow month must be no more than {APP_CONFIG['max_time_horizon']}")
    
    # Validate description (optional)
    if description and len(description) > 100:
        errors.append("Cashflow description must be 100 characters or less")
    
    result = {
        'valid': len(errors) == 0,
        'errors': errors
    }
    
    if errors:
        logger.debug(f"Cashflow input validation failed: {errors}")
    
    return result

def validate_data_consistency(
    time_horizon: int,
    cashflows: List[Any]
) -> Dict[str, Any]:
    """
    Validate data consistency across inputs.
    
    Args:
        time_horizon: Forecast time horizon
        cashflows: List of cashflow items
        
    Returns:
        Dictionary with validation results and error messages
    """
    errors = []
    
    # Check if any cashflows occur after the time horizon
    for i, cashflow in enumerate(cashflows):
        if hasattr(cashflow, 'month') and cashflow.month > time_horizon:
            errors.append(
                f"Cashflow #{i+1} occurs after the forecast period "
                f"(month {cashflow.month} > {time_horizon})"
            )
    
    # Check for too many cashflows
    if len(cashflows) > APP_CONFIG['max_cashflows']:
        errors.append(f"Maximum {APP_CONFIG['max_cashflows']} cashflows allowed")
    
    result = {
        'valid': len(errors) == 0,
        'errors': errors
    }
    
    if errors:
        logger.warning(f"Data consistency validation failed: {errors}")
    
    return result

def validate_date_inputs(
    group_code: Optional[str],
    start_date: Optional[date],
    end_date: Optional[date]
) -> Dict[str, Any]:
    """
    Validate date input parameters for database queries.
    
    Args:
        group_code: Portfolio group identifier
        start_date: Period start date
        end_date: Period end date
        
    Returns:
        Dictionary with validation results and error messages
    """
    errors = []
    
    # Validate group code
    if not group_code or not group_code.strip():
        errors.append("Group code is required")
    elif len(group_code.strip()) > 50:
        errors.append("Group code must be 50 characters or less")
    
    # Validate dates
    if start_date is None:
        errors.append("Start date is required")
    
    if end_date is None:
        errors.append("End date is required")
    
    if start_date and end_date:
        # Check date order
        if start_date >= end_date:
            errors.append("Start date must be before end date")
        
        # Check date range (not too far in the past or future)
        today = date.today()
        max_past_date = today - timedelta(days=365 * 10)  # 10 years ago
        max_future_date = today + timedelta(days=365 * 2)  # 2 years in future
        
        if start_date < max_past_date:
            errors.append("Start date cannot be more than 10 years in the past")
        
        if end_date > max_future_date:
            errors.append("End date cannot be more than 2 years in the future")
        
        # Check minimum period length (at least 1 day)
        if (end_date - start_date).days < 1:
            errors.append("Period must be at least 1 day long")
    
    result = {
        'valid': len(errors) == 0,
        'errors': errors
    }
    
    if errors:
        logger.warning(f"Date input validation failed: {errors}")
    
    return result
