from typing import List, Tuple
import os
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
from database_connection import DatabaseConnection
from datetime import datetime, date


class DataManager:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_market_values(self, group_code: str, start_date: datetime.date, end_date: datetime.date) -> Tuple[float, float]:
        query = f"""
        SELECT
            SUM(CASE WHEN date = '{start_date}' THEN amount_rc ELSE 0 END) as beginning_mv,
            SUM(CASE WHEN date = '{end_date}' THEN amount_rc ELSE 0 END) as ending_mv
        FROM IPD.ClientHolding  
        WHERE group_code = '{group_code}' AND date IN ('{start_date}', '{end_date}')
        """
        result = self.db_connection.call_db(query)
        #print("get market value bmv: " + result['beginning_mv'].iloc[0])
        #print("get marekt value emv: " + result['ending_mv'].iloc[0])
        return result['beginning_mv'].iloc[0], result['ending_mv'].iloc[0]

    def get_cashflows(self, group_code: str, start_date: datetime.date, end_date: datetime.date) -> List[Tuple[datetime.date, float]]:
        query = f"""
        SELECT date, SUM(amount_rc) amount_rc
        FROM IPD.ClientCashFlow
        WHERE group_code = '{group_code}' AND date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY date
        ORDER BY date
        """
        result = self.db_connection.call_db(query)
        return list(zip(result['date'], result['amount_rc']))
