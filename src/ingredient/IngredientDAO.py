import pyodbc
from ingredient.IngredientDTO import IngredientDTO


class IngredientDAO:
    def get_all_ingredients(self):
        conn = self.database_config()
        cursor = conn.cursor()

        cursor.execute("SELECT ma_thanh_phan, ten_thanh_phan FROM ThanhPhan")
        rows = cursor.fetchall()

        ingredients = []
        for row in rows:
            ingredient = IngredientDTO(row.ma_thanh_phan, row.ten_thanh_phan)
            ingredients.append(ingredient)

        conn.close()
        return ingredients

    def get_ingredient_id_by_name(self, ingredient_name):
        conn = self.database_config()
        cursor = conn.cursor()

        cursor.execute("SELECT ma_thanh_phan FROM ThanhPhan WHERE ten_thanh_phan = ?", (ingredient_name,))
        row = cursor.fetchone()

        conn.close()

        if row is not None:
            return row.ma_thanh_phan
        return None