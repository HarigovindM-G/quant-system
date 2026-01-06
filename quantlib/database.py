"""
Database utility module for SQLite operations
"""
import pandas as pd
import sqlite3
from sqlalchemy import create_engine, text
import os


class Database:
    """SQLite database handler for storing and retrieving trading data"""
    
    def __init__(self, db_path='Data/hakuquant.db'):
        """
        Initialize SQLite connection
        
        Args:
            db_path: Path to SQLite database file (default: Data/hakuquant.db)
        """
        self.db_path = db_path
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Create SQLite engine
        self.connection_string = f"sqlite:///{db_path}"
        self.engine = create_engine(self.connection_string)
        
        print(f"Connected to SQLite database: {db_path}")
    
    def save_dataframe(self, df, table_name, if_exists='replace'):
        """
        Save pandas DataFrame to SQLite table
        
        Args:
            df: pandas DataFrame to save
            table_name: Name of the table
            if_exists: 'fail', 'replace', or 'append'
        """
        try:
            df.to_sql(table_name, self.engine, if_exists=if_exists, index=True)
            print(f"✓ Saved {len(df)} rows to table '{table_name}' in {self.db_path}")
        except Exception as e:
            print(f"✗ Error saving to SQLite: {str(e)}")
            raise
    
    def load_dataframe(self, table_name, query=None):
        """
        Load data from SQLite table into pandas DataFrame
        
        Args:
            table_name: Name of the table to load
            query: Optional SQL query (if None, loads entire table)
        
        Returns:
            pandas DataFrame
        """
        try:
            if query:
                df = pd.read_sql(query, self.engine)
            else:
                df = pd.read_sql(f"SELECT * FROM {table_name}", self.engine, index_col='date')
            print(f"✓ Loaded {len(df)} rows from table '{table_name}'")
            return df
        except Exception as e:
            print(f"✗ Error loading from SQLite: {str(e)}")
            raise
    
    def table_exists(self, table_name):
        """Check if a table exists in the database"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                )
                return result.fetchone() is not None
        except Exception as e:
            print(f"Error checking table existence: {str(e)}")
            return False
    
    def list_tables(self):
        """List all tables in the database"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table'")
                )
                tables = [row[0] for row in result.fetchall()]
                return tables
        except Exception as e:
            print(f"Error listing tables: {str(e)}")
            return []
    
    def get_table_info(self, table_name):
        """Get column information for a table"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"PRAGMA table_info({table_name})"))
                columns = [row[1] for row in result.fetchall()]
                return columns
        except Exception as e:
            print(f"Error getting table info: {str(e)}")
            return []
    
    def close(self):
        """Close database connection"""
        self.engine.dispose()
        print(f"✓ Database connection closed")

