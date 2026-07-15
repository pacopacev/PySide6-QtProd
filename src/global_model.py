import pandas as pd
import psycopg2
from datetime import datetime
import os
from pathlib import Path



class GlobalModel:
    def __init__(self):
        
        self.user_id = None
        self.conn = None
        
        print("GlobalModel initialized")
        self.db_config = {
            'host': 'pg-143cbe8e-pacopacev277-7915.e.aivencloud.com',
            'database': 'defaultdb',
            'user': 'avnadmin', 
            'password': 'AVNS_LqW5lU_kmJDiLuips8n',
            'port': 11821,
            'sslmode': 'require'
        }        
        self.conn = self.connect_db()
        
        # СЕТЪР метод за записване
    def set_user_id(self, user_id):
        self._user_id = user_id
        print(f"[GlobalModel] Успешно записано ID: {self._user_id}")

    # ГЕТЪР метод за взимане
    def get_user_id(self):
        return self._user_id
    
    
    
    
    
        
    
    def connect_db(self):
        """Creates or restores a live database connection"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            return self.conn
        except Exception as e:
            self.log(f"Failed to connect directly to Aiven Cloud: {e}", "ERROR")
            self.conn = None
            return None 
    def log(self, message, type="INFO"):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            print(f"[{timestamp}] [{type}] {message}")
        except OSError:
            pass  # Handle cases where the output stream is closed or unavailable
        
        
    def safe_bool(self, value):
        """Safely convert to boolean"""
        if value is None or pd.isna(value):
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', 'yes', '1', 't', 'y']
        try:
            return bool(value)
        except:
            return False    
    def safe_int(self, value, default=0):
        """Safely convert to integer"""
        if value is None or pd.isna(value):
            return default
        try:
            return int(float(value))
        except:
            return default    
    def safe_float(self, value, default=None):
        if value is None or pd.isna(value):
            return default
        try:
            return float(value)
        except:
            return default    
    def safe_str(self, value, default=None):    
        if value is None or pd.isna(value):
            return default
        try:
            return str(value)
        except:
            return default   
    def safe_date(self, value, default=None):
        if value is None or pd.isna(value):
            return default
        if isinstance(value, datetime):
            return value.date()
        try:
            return pd.to_datetime(value).date()
        except:
            return default
        
    def close_connection(self):
        """Safely closes the connection if it exists"""
        # Remove or guard any self.cursor references here
        try:
            if hasattr(self, 'conn') and self.conn is not None:
                if getattr(self.conn, 'closed', 0) == 0:
                    self.conn.close()
                self.conn = None
            print("Database connection closed cleanly.")
        except Exception as e:
            print(f"Error while closing connection: {e}")

    def __del__(self):
        """Destructor to clean up resources when the object is destroyed"""
        self.close_connection()
                   




