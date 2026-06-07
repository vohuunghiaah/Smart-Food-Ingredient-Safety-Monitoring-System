import pyodbc
def database_config():
    return pyodbc.connect(
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=DESKTOP-J0H3193\\SQLEXPRESS;"  
        "Database=FOOD;" 
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )