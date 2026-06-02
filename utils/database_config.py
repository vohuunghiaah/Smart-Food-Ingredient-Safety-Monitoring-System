import pyodbc
def database_config():
    return pyodbc.connect(
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=LAPTOP-INA5QMN2\\MSSQLSERVER01;"  # Điền thẳng ở đây
        "Database=FOOD;"                         # Điền thẳng ở đây
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )