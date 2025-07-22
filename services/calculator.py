"""
Portfolio calculation services for BCI Nowcasting Tool.

Handles future value calculations, scenario analysis, and portfolio projections.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)

@dataclass
class CashflowItem:
    """Represents a single cashflow item."""
    amount: float
    month: int
    description: str = ""

@dataclass
class CashflowFVItem:
    """Represents the future value of a single cashflow item."""
    amount: float
    month: int
    description: str
    fv_downside: float
    fv_base: float
    fv_upside: float

@dataclass
class ScenarioResult:
    """Represents the result of a scenario calculation."""
    portfolio_fv: float
    cashflow_fv: float
    total_fv: float
    rate: float
    scenario_name: str
    cashflow_details: Optional[List['CashflowFVItem']] = None

class PortfolioCalculator:
    """Handles portfolio valuation calculations and scenario analysis."""
    
    def __init__(self):
        """Initialize the portfolio calculator."""
        logger.info("Initialized PortfolioCalculator")
    
    def calculate_future_value(self, present_value: float, annual_rate: float, months: int) -> float:
        """
        Calculate future value using compound interest.
        
        Args:
            present_value: Starting value
            annual_rate: Annual interest rate as percentage (e.g., 7 for 7%)
            months: Number of months to compound
            
        Returns:
            Future value after compounding
        """
        if annual_rate == 0:
            return present_value
        
        monthly_rate = annual_rate / 100 / 12
        future_value = present_value * ((1 + monthly_rate) ** months)
        
        logger.debug(f"FV calculation: PV={present_value}, rate={annual_rate}%, months={months}, FV={future_value}")
        return future_value
    
    def calculate_cashflow_future_value(
        self, 
        cashflow: CashflowItem, 
        annual_rate: float, 
        total_months: int
    ) -> float:
        """
        Calculate the future value of a single cashflow.
        
        Args:
            cashflow: The cashflow item
            annual_rate: Annual growth rate as percentage
            total_months: Total forecast period in months
            
        Returns:
            Future value of the cashflow
        """
        months_to_grow = total_months - cashflow.month
        
        if months_to_grow <= 0:
            # Cashflow occurs at or after the end date
            return cashflow.amount
        
        return self.calculate_future_value(cashflow.amount, annual_rate, months_to_grow)
    
    def calculate_total_cashflow_fv(
        self, 
        cashflows: List[CashflowItem], 
        annual_rate: float, 
        total_months: int
    ) -> float:
        """
        Calculate the total future value of all cashflows.
        
        Args:
            cashflows: List of cashflow items
            annual_rate: Annual growth rate as percentage
            total_months: Total forecast period in months
            
        Returns:
            Total future value of all cashflows
        """
        total_fv = 0.0
        
        for cashflow in cashflows:
            if cashflow.amount != 0:  # Skip zero cashflows
                cf_fv = self.calculate_cashflow_future_value(cashflow, annual_rate, total_months)
                total_fv += cf_fv
                logger.debug(f"Cashflow FV: month={cashflow.month}, amount={cashflow.amount}, fv={cf_fv}")
        
        logger.debug(f"Total cashflow FV: {total_fv}")
        return total_fv
    
    def calculate_scenario(
        self,
        beginning_mv: float,
        time_horizon: int,
        annual_rate: float,
        cashflows: List[CashflowItem],
        scenario_name: str
    ) -> ScenarioResult:
        """
        Calculate a single scenario result.
        
        Args:
            beginning_mv: Starting market value
            time_horizon: Forecast period in months
            annual_rate: Annual return rate as percentage
            cashflows: List of future cashflows
            scenario_name: Name of the scenario
            
        Returns:
            ScenarioResult with calculated values
        """
        try:
            # Calculate portfolio future value
            portfolio_fv = self.calculate_future_value(beginning_mv, annual_rate, time_horizon)
            
            # Calculate cashflow future values
            cashflow_fv = self.calculate_total_cashflow_fv(cashflows, annual_rate, time_horizon)
            
            # Calculate total future value
            total_fv = portfolio_fv + cashflow_fv
            
            result = ScenarioResult(
                portfolio_fv=portfolio_fv,
                cashflow_fv=cashflow_fv,
                total_fv=total_fv,
                rate=annual_rate,
                scenario_name=scenario_name
            )
            
            logger.info(f"Calculated {scenario_name} scenario: Total FV = {total_fv:,.0f}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating {scenario_name} scenario: {str(e)}")
            raise
    
    def calculate_all_scenarios(
        self,
        beginning_mv: float,
        time_horizon: int,
        scenarios: Dict[str, float],
        cashflows: List[CashflowItem]
    ) -> Dict[str, ScenarioResult]:
        """
        Calculate all scenario results with detailed cashflow analysis.
        
        Args:
            beginning_mv: Starting market value
            time_horizon: Forecast period in months
            scenarios: Dictionary of scenario names to annual rates
            cashflows: List of future cashflows
            
        Returns:
            Dictionary of scenario results with detailed cashflow future values
        """
        results = {}
        
        # First, calculate future values for each cashflow under all scenarios
        cashflow_fv_details = []
        for cashflow in cashflows:
            fv_downside = self.calculate_cashflow_future_value(cashflow, scenarios.get('downside', 0), time_horizon)
            fv_base = self.calculate_cashflow_future_value(cashflow, scenarios.get('base', 0), time_horizon)
            fv_upside = self.calculate_cashflow_future_value(cashflow, scenarios.get('upside', 0), time_horizon)
            
            cashflow_fv_details.append(CashflowFVItem(
                amount=cashflow.amount,
                month=cashflow.month,
                description=cashflow.description,
                fv_downside=fv_downside,
                fv_base=fv_base,
                fv_upside=fv_upside
            ))
        
        # Now calculate results for each scenario
        for scenario_name, annual_rate in scenarios.items():
            try:
                # Calculate portfolio future value
                portfolio_fv = self.calculate_future_value(beginning_mv, annual_rate, time_horizon)
                
                # Sum cashflow future values for this scenario
                total_cashflow_fv = 0.0
                for cf_detail in cashflow_fv_details:
                    if scenario_name == 'downside':
                        total_cashflow_fv += cf_detail.fv_downside
                    elif scenario_name == 'base':
                        total_cashflow_fv += cf_detail.fv_base
                    elif scenario_name == 'upside':
                        total_cashflow_fv += cf_detail.fv_upside
                
                # Create scenario result
                total_fv = portfolio_fv + total_cashflow_fv
                
                results[scenario_name] = ScenarioResult(
                    portfolio_fv=portfolio_fv,
                    cashflow_fv=total_cashflow_fv,
                    total_fv=total_fv,
                    rate=annual_rate,
                    scenario_name=scenario_name,
                    cashflow_details=cashflow_fv_details
                )
                
            except Exception as e:
                logger.error(f"Failed to calculate scenario {scenario_name}: {str(e)}")
                continue
        
        logger.info(f"Calculated {len(results)} scenarios with detailed cashflows")
        return results
    
    def get_forecast_end_date(self, time_horizon: int) -> datetime:
        """
        Calculate the forecast end date.
        
        Args:
            time_horizon: Number of months in the future
            
        Returns:
            End date of the forecast period
        """
        today = datetime.now()
        end_date = today + relativedelta(months=time_horizon)
        return end_date
