import pyodbc
def database_config():
    return pyodbc.connect(
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=DESKTOP-1PJL28F;"  
        "Database=AllergyDB;" 
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )