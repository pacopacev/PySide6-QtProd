import pandas as pd
from psycopg2 import pool
from psycopg2.extensions import TRANSACTION_STATUS_IDLE
from datetime import datetime
import os
from threading import Lock
from dotenv import load_dotenv

load_dotenv()



class GlobalModel:
    MIN_CONNECTIONS = 1
    MAX_CONNECTIONS = 5
    _db_pool = None
    _db_pool_lock = Lock()

    def __init__(self):
        self._user_id = None
        self.conn = None
        
        print("GlobalModel initialized")
        self.db_config = {
            'host': os.getenv("DB_HOST"),
            'database': os.getenv("DB_NAME"),
            'user': os.getenv("DB_USER"),
            'password': os.getenv("DB_PASSWORD"),
            'port': os.getenv("DB_PORT", "11821"),
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
    
    
    
    
    
    @classmethod
    def _get_pool(cls, db_config):
        """Create the shared pool on first use."""
        with cls._db_pool_lock:
            if cls._db_pool is None:
                cls._db_pool = pool.ThreadedConnectionPool(
                    cls.MIN_CONNECTIONS,
                    cls.MAX_CONNECTIONS,
                    **db_config
                )
            return cls._db_pool

    def connect_db(self):
        """Borrow a connection from the shared pool."""
        try:
            db_pool = self._get_pool(self.db_config)
            if self.conn is not None:
                if self.conn.closed == 0:
                    return self.conn
                db_pool.putconn(self.conn, close=True)
                self.conn = None

            self.conn = db_pool.getconn()
            return self.conn
        except Exception as e:
            self.log(f"Failed to get a database connection: {e}", "ERROR")
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

    def safe_datetime(self, value, default=None):
        if value is None or pd.isna(value):
            return default or datetime.now()
        if isinstance(value, datetime):
            return value
        if isinstance(value, pd.Timestamp):
            return value.to_pydatetime()
        try:
            return pd.to_datetime(value).to_pydatetime()
        except:
            return default or datetime.now()
        
    def close_connection(self):
        """Return the borrowed connection to the pool."""
        conn = self.conn
        self.conn = None
        if conn is None:
            return

        db_pool = type(self)._db_pool
        try:
            if conn.closed:
                if db_pool is not None:
                    db_pool.putconn(conn, close=True)
                return

            if conn.get_transaction_status() != TRANSACTION_STATUS_IDLE:
                conn.rollback()

            if db_pool is None:
                conn.close()
            else:
                db_pool.putconn(conn)
            print("Database connection returned to the pool.")
        except Exception as e:
            self.log(f"Error while returning the database connection: {e}", "ERROR")
            if not conn.closed:
                conn.close()

    @classmethod
    def close_all_connections(cls):
        """Close all pooled connections when the application exits."""
        with cls._db_pool_lock:
            db_pool = cls._db_pool
            cls._db_pool = None

        if db_pool is not None:
            db_pool.closeall()

    def __del__(self):
        """Destructor to clean up resources when the object is destroyed"""
        self.close_connection()
                   

