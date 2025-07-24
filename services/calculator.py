"""
Portfolio calculation services for BCI Nowcasting Tool.

Handles future value calculations, scenario analysis, and portfolio projections.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)

@dataclass
class CashflowItem:
    """Represents a single cashflow item."""
    amount: float
    month: int
    description: str = ""
    cashflow_date: Optional[date] = None

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
    
    def calculate_future_value_excel_formula(
        self, 
        present_value: float, 
        annual_rate: float, 
        start_date: date, 
        end_date: date
    ) -> float:
        """
        Calculate future value using Excel formula: =PV*(1+rate)^((end_date-start_date)/365)
        
        Args:
            present_value: Starting value (C271 in Excel)
            annual_rate: Annual interest rate as percentage (F$2 in Excel, converted to decimal)
            start_date: Starting date (A271 in Excel - cashflow date)
            end_date: End date (B$1 in Excel - period end date)
            
        Returns:
            Future value after compounding using Excel formula
        """
        if annual_rate == 0:
            return present_value
        
        # Convert percentage to decimal (Excel uses decimal rates)
        rate_decimal = annual_rate / 100
        
        # Calculate days difference (B$1 - A271)
        days_diff = (end_date - start_date).days
        
        # Excel formula: =C271*(1+F$2)^((B$1-A271)/365)
        future_value = present_value * ((1 + rate_decimal) ** (days_diff / 365))
        
        logger.debug(f"Excel FV calculation: PV={present_value}, rate={annual_rate}%, days={days_diff}, FV={future_value}")
        return future_value
    
    def calculate_future_value(self, present_value: float, annual_rate: float, months: int) -> float:
        """
        Legacy monthly compound calculation - kept for backward compatibility.
        """
        if annual_rate == 0:
            return present_value
        
        monthly_rate = annual_rate / 100 / 12
        future_value = present_value * ((1 + monthly_rate) ** months)
        
        logger.debug(f"Monthly FV calculation: PV={present_value}, rate={annual_rate}%, months={months}, FV={future_value}")
        return future_value
    
    def calculate_cashflow_future_value_excel(
        self, 
        cashflow: CashflowItem, 
        annual_rate: float, 
        end_date: date
    ) -> float:
        """
        Calculate the future value of a single cashflow using Excel formula.
        Formula: =C271*(1+F$2)^((B$1-A271)/365)
        
        Args:
            cashflow: The cashflow item with amount and date
            annual_rate: Annual growth rate as percentage (F$2)
            end_date: Period end date (B$1)
            
        Returns:
            Future value of the cashflow using Excel formula
        """
        if not cashflow.cashflow_date:
            # Fallback to month-based calculation if no date available
            return cashflow.amount
        
        # If cashflow occurs at or after end date, no growth
        if cashflow.cashflow_date >= end_date:
            return cashflow.amount
        
        # Use Excel formula: =C271*(1+F$2)^((B$1-A271)/365)
        return self.calculate_future_value_excel_formula(
            cashflow.amount,  # C271
            annual_rate,      # F$2 
            cashflow.cashflow_date,  # A271
            end_date         # B$1
        )
    
    def calculate_cashflow_future_value(
        self, 
        cashflow: CashflowItem, 
        annual_rate: float, 
        total_months: int
    ) -> float:
        """
        Legacy monthly-based cashflow calculation - kept for backward compatibility.
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
    
    def calculate_scenario_excel(
        self,
        beginning_mv: float,
        start_date: date,
        end_date: date,
        annual_rate: float,
        cashflows: List[CashflowItem],
        scenario_name: str
    ) -> ScenarioResult:
        """
        Calculate a single scenario result using Excel formula approach.
        
        Args:
            beginning_mv: Starting market value
            start_date: Period start date
            end_date: Period end date (B$1 in Excel)
            annual_rate: Annual return rate as percentage
            cashflows: List of future cashflows with dates
            scenario_name: Name of the scenario
            
        Returns:
            ScenarioResult with calculated values using Excel formula
        """
        try:
            # Calculate portfolio future value using Excel formula
            portfolio_fv = self.calculate_future_value_excel_formula(
                beginning_mv, annual_rate, start_date, end_date
            )
            
            # Calculate cashflow future values using Excel formula
            cashflow_fv = 0.0
            for cashflow in cashflows:
                if cashflow.amount != 0:  # Skip zero cashflows
                    cf_fv = self.calculate_cashflow_future_value_excel(cashflow, annual_rate, end_date)
                    cashflow_fv += cf_fv
                    logger.debug(f"Excel CF FV: date={cashflow.cashflow_date}, amount={cashflow.amount}, fv={cf_fv}")
            
            # Calculate total future value
            total_fv = portfolio_fv + cashflow_fv
            
            result = ScenarioResult(
                portfolio_fv=portfolio_fv,
                cashflow_fv=cashflow_fv,
                total_fv=total_fv,
                rate=annual_rate,
                scenario_name=scenario_name
            )
            
            logger.info(f"Calculated {scenario_name} scenario (Excel formula): Total FV = {total_fv:,.0f}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating {scenario_name} scenario with Excel formula: {str(e)}")
            raise
    
    def calculate_scenario(
        self,
        beginning_mv: float,
        time_horizon: int,
        annual_rate: float,
        cashflows: List[CashflowItem],
        scenario_name: str
    ) -> ScenarioResult:
        """
        Legacy monthly-based scenario calculation - kept for backward compatibility.
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
    
    def calculate_all_scenarios_excel(
        self,
        beginning_mv: float,
        start_date: date,
        end_date: date,
        scenarios: Dict[str, float],
        cashflows: List[CashflowItem]
    ) -> Dict[str, ScenarioResult]:
        """
        Calculate all scenario results using Excel formula approach.
        
        Args:
            beginning_mv: Starting market value
            start_date: Period start date
            end_date: Period end date (B$1 in Excel)
            scenarios: Dictionary of scenario names to annual rates
            cashflows: List of future cashflows with dates
            
        Returns:
            Dictionary of scenario results using Excel formula calculations
        """
        results = {}
        
        # First, calculate future values for each cashflow under all scenarios using Excel formula
        cashflow_fv_details = []
        for cashflow in cashflows:
            fv_downside = self.calculate_cashflow_future_value_excel(cashflow, scenarios.get('downside', 0), end_date)
            fv_base = self.calculate_cashflow_future_value_excel(cashflow, scenarios.get('base', 0), end_date)
            fv_upside = self.calculate_cashflow_future_value_excel(cashflow, scenarios.get('upside', 0), end_date)
            
            cashflow_fv_details.append(CashflowFVItem(
                amount=cashflow.amount,
                month=cashflow.month,
                description=cashflow.description,
                fv_downside=fv_downside,
                fv_base=fv_base,
                fv_upside=fv_upside
            ))
        
        # Now calculate results for each scenario using Excel formula
        for scenario_name, annual_rate in scenarios.items():
            try:
                # Calculate portfolio future value using Excel formula
                portfolio_fv = self.calculate_future_value_excel_formula(beginning_mv, annual_rate, start_date, end_date)
                
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
                logger.error(f"Failed to calculate scenario {scenario_name} with Excel formula: {str(e)}")
                continue
        
        logger.info(f"Calculated {len(results)} scenarios using Excel formula with detailed cashflows")
        return results
    
    def calculate_all_scenarios(
        self,
        beginning_mv: float,
        time_horizon: int,
        scenarios: Dict[str, float],
        cashflows: List[CashflowItem]
    ) -> Dict[str, ScenarioResult]:
        """
        Legacy monthly-based calculation - kept for backward compatibility.
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
