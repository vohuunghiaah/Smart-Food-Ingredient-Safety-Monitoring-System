import os
import pyodbc
from dotenv import load_dotenv

load_dotenv(dotenv_path="parameter.env")

def get_connection():
    """
    Tạo và trả về một kết nối tới SQL Server.
    Sử dụng Windows Authentication (Trusted_Connection).
    """
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_DATABASE")
    return pyodbc.connect(
        f"Driver={{ODBC Driver 17 for SQL Server}};"
        f"Server={server};"
        f"Database={database};"
        f"Trusted_Connection=yes;"
        f"TrustServerCertificate=yes;"
    )