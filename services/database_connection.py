import os
import time
import configparser
import pandas as pd
import pyodbc

pd.set_option('display.max_columns', None)

class DatabaseConnection:
    def __init__(self):
        # Database configuration - hardcoded values, will switch to AnalyticsPerformance when ready
        db_host = "bcinvestment-sqlmi-adp-pro-01.f89163b05af0.database.windows.net"
        db_name = "RawAMR" 
        
        self.connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={db_host};"
            f"DATABASE={db_name};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=no;"
            f"Connection Timeout=30;"
            f"Authentication=ActiveDirectoryInteractive;"
        )
        
        print(f"Connection string: {self.connection_string}")
        
    def _get_connection(self):
        """Get a fresh database connection"""
        try:
            return pyodbc.connect(self.connection_string)
        except Exception as e:
            print(f"Failed to establish database connection: {e}")
            raise

    # Construct query from file
    def construct_query(self, query_file, params=None):
        # Read the SQL file as a string
        with open(query_file, 'r') as file:
            query = file.read()
        
        # Add the parameters to the query if provided
        if params:
            query = params + query
        
        return query

    # Construct query from string
    def construct_query_str(self, query_str, params=None):
        if params:
            query = params + query_str
        else:
            query = query_str
        return query

    def call_db(self, query):
        """Execute query using pure pyodbc - same as working test script"""
        t0 = time.time()
        conn = None
        try:
            # Get fresh connection for each query
            conn = self._get_connection()
            
            # Execute query using pandas read_sql_query (most reliable method)
            df = pd.read_sql_query(query, conn)
            
            t1 = time.time()
            print('Query completed in', round(t1 - t0, 3), 'seconds')
            
            return df
        
        except Exception as e:
            print('Error while running the query:', e)
            raise
        finally:
            if conn:
                conn.close()
