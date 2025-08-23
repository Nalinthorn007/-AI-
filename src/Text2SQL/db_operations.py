import pandas as pd 
from typing import Dict, Any
from config_db.db_warehouse import get_db_connection

class DatabaseOperations:
    def __init__(self):
        """
        Initialize Database Operations
        """
        self.connection = None
    
    def connect(self) -> bool:
        """
        Establish database connection
        """
        try:
            self.connection = get_db_connection()
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False
    
    def disconnect(self):
        """
        Close database connection
        """
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, sql_query: str) -> Dict[str, Any]:
        """
        Execute SQL query and return results
        """
        if not self.connection:
            if not self.connect():
                return {"error": "Database connection failed"}
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql_query)
            
            # Check if it's a SELECT query
            if sql_query.strip().upper().startswith('SELECT'):
                # Fetch results
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                # Convert to DataFrame
                df = pd.DataFrame(rows, columns=columns)
                
                return {
                    "success": True,
                    "data": df,
                    "row_count": len(df),
                    "columns": columns
                }
            else:
                # For non-SELECT queries
                self.connection.commit()
                return {
                    "success": True,
                    "message": f"Query executed successfully. Rows affected: {cursor.rowcount}",
                    "row_count": cursor.rowcount
                }
                
        except Exception as e:
            return {
                "error": f"Query execution failed: {str(e)}",
                "sql": sql_query
            }
        finally:
            if cursor:
                cursor.close()
    
    def get_table_schema(self) -> str:
        """
        Get database schema information as a string
        """
        if not self.connection:
            if not self.connect():
                return "Database connection failed"
        
        try:
            cursor = self.connection.cursor()
            
            # Get all tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            schema_info = "Database Schema:\n"
            for table in tables:
                table_name = table[0]
                schema_info += f"\nTable: {table_name}\n"
                
                # Get table structure
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                
                for col in columns:
                    schema_info += f"  - {col[0]}: {col[1]}"
                    if col[2] == 'NO':
                        schema_info += " (NOT NULL)"
                    if col[3] == 'PRI':
                        schema_info += " (PRIMARY KEY)"
                    schema_info += "\n"
            
            return schema_info
                
        except Exception as e:
            return f"Schema retrieval failed: {str(e)}"
        finally:
            if cursor:
                cursor.close()
    
    def test_connection(self) -> bool:
        """
        Test database connection
        """
        try:
            if self.connect():
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1 as test")
                cursor.fetchone()
                cursor.close()
                return True
            return False
        except:
            return False 