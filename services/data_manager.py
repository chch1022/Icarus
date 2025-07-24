"""
Data management services for BCI Nowcasting Tool.

Handles database operations for retrieving market values and cashflows.
"""

from typing import List, Tuple
import os
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import logging

from services.database_connection import DatabaseConnection

logger = logging.getLogger(__name__)

class DataManager:
    """Manages database operations for portfolio data retrieval."""
    
    def __init__(self):
        """Initialize the data manager with database connection."""
        self.db_connection = DatabaseConnection()
        logger.info("Initialized DataManager")

    def get_market_values(self, group_code: str, start_date: datetime.date, end_date: datetime.date) -> Tuple[float, float]:
        """
        Retrieve beginning and ending market values for a portfolio.
        
        Args:
            group_code: Portfolio group identifier
            start_date: Period start date
            end_date: Period end date
            
        Returns:
            Tuple of (beginning_mv, ending_mv)
        """
        try:
            query = f"""
            SELECT
                SUM(CASE WHEN date = '{start_date}' THEN market_value_rc ELSE 0 END) as beginning_mv,
                SUM(CASE WHEN date = '{end_date}' THEN market_value_rc ELSE 0 END) as ending_mv
            FROM "IPD"."ClientHolding"  
            WHERE group_code = '{group_code}' AND date IN ('{start_date}', '{end_date}')
            """
            
            result = self.db_connection.call_db(query)
            
            beginning_mv = float(result['beginning_mv'].iloc[0] or 0)
            ending_mv = float(result['ending_mv'].iloc[0] or 0)
            
            logger.info(f"Retrieved market values for {group_code}: BMV={beginning_mv:,.2f}, EMV={ending_mv:,.2f}")
            return beginning_mv, ending_mv
            
        except Exception as e:
            logger.error(f"Error retrieving market values for {group_code}: {str(e)}")
            raise

    def get_cashflows(self, group_code: str, start_date: datetime.date, end_date: datetime.date) -> List:
        """
        Retrieve cashflow data for a portfolio within a date range.
        
        Args:
            group_code: Portfolio group identifier
            start_date: Period start date
            end_date: Period end date
            
        Returns:
            List of CashflowItem objects
        """
        try:
            from services.calculator import CashflowItem
            
            query = f"""
            SELECT date, SUM(amount_rc) amount_rc
            FROM "IPD"."ClientCashFlow"
            WHERE group_code = '{group_code}' AND date BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY date
            ORDER BY date
            """
            
            result = self.db_connection.call_db(query)
            
            # Convert database results to CashflowItem objects
            cashflows = []
            for i in range(len(result)):
                cashflow_date = result['date'].iloc[i]
                amount = result['amount_rc'].iloc[i]
                
                # Calculate months from start_date to cashflow_date
                if isinstance(cashflow_date, str):
                    from datetime import datetime
                    cashflow_date = datetime.strptime(cashflow_date, '%Y-%m-%d').date()
                
                months_diff = (cashflow_date.year - start_date.year) * 12 + (cashflow_date.month - start_date.month)
                
                cashflow_item = CashflowItem(
                    amount=float(amount),
                    month=max(1, months_diff + 1),  # Ensure month is at least 1
                    description=f"Cashflow on {cashflow_date}",
                    cashflow_date=cashflow_date
                )
                cashflows.append(cashflow_item)
            
            logger.info(f"Retrieved {len(cashflows)} cashflows for {group_code}")
            return cashflows
            
        except Exception as e:
            logger.error(f"Error retrieving cashflows for {group_code}: {str(e)}")
            raise

    def validate_group_code(self, group_code: str) -> bool:
        """
        Validate if a group code exists in the database.
        
        Args:
            group_code: Portfolio group identifier to validate
            
        Returns:
            True if group code exists, False otherwise
        """
        try:
            query = f"""
            SELECT COUNT(*) as count
            FROM IPD.ClientHolding
            WHERE group_code = '{group_code}'
            LIMIT 1
            """
            
            result = self.db_connection.call_db(query)
            exists = result['count'].iloc[0] > 0
            
            logger.debug(f"Group code {group_code} validation: {'exists' if exists else 'not found'}")
            return exists
            
        except Exception as e:
            logger.error(f"Error validating group code {group_code}: {str(e)}")
            return False

    def get_available_date_range(self, group_code: str) -> Tuple[datetime.date, datetime.date]:
        """
        Get the available date range for a group code.
        
        Args:
            group_code: Portfolio group identifier
            
        Returns:
            Tuple of (min_date, max_date) available for the group
        """
        try:
            query = f"""
            SELECT 
                MIN(date) as min_date,
                MAX(date) as max_date
            FROM IPD.ClientHolding
            WHERE group_code = '{group_code}'
            """
            
            result = self.db_connection.call_db(query)
            min_date = result['min_date'].iloc[0]
            max_date = result['max_date'].iloc[0]
            
            logger.debug(f"Available date range for {group_code}: {min_date} to {max_date}")
            return min_date, max_date
            
        except Exception as e:
            logger.error(f"Error retrieving date range for {group_code}: {str(e)}")
            raise

    def calculate_time_horizon_months(self, start_date: datetime.date, end_date: datetime.date) -> int:
        """
        Calculate the number of months between two dates.
        
        Args:
            start_date: Period start date
            end_date: Period end date
            
        Returns:
            Number of months between dates
        """
        try:
            # Calculate the difference in months
            months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            
            # Add partial month if end day is later than start day
            if end_date.day > start_date.day:
                months += 1
            
            logger.debug(f"Time horizon: {start_date} to {end_date} = {months} months")
            return max(1, months)  # Ensure at least 1 month
            
        except Exception as e:
            logger.error(f"Error calculating time horizon: {str(e)}")
            return 1