import pyodbc
from IngredientDTO import IngredientDTO

class IngredientDAO:
    def get_connection(self):
        return pyodbc.connect(
            r'Driver={ODBC Driver 17 for SQL Server};'
            r'Server=MSI\SQLEXPRESS;'
            r'Database=FOOD;'
            r'Trusted_Connection=yes;'
            r'TrustServerCertificate=yes;'
        )

    def get_all_ingredients(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT ma_thanh_phan, ten_thanh_phan FROM ThanhPhan")
        rows = cursor.fetchall()

        ingredients = []
        for row in rows:
            ingredient = IngredientDTO(row.ma_thanh_phan, row.ten_thanh_phan)
            ingredients.append(ingredient)

        conn.close()
        return ingredients