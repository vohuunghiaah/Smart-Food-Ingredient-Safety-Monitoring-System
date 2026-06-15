import pyodbc
from ingredient.IngredientDTO import IngredientDTO
from utils.database_config import database_config

class IngredientDAO:
    def get_all_ingredients(self):

        conn = database_config()
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

        conn = database_config()
        cursor = conn.cursor()

        cursor.execute("SELECT ma_thanh_phan FROM ThanhPhan WHERE ten_thanh_phan = ?", (ingredient_name,))
        row = cursor.fetchone()

        conn.close()

        if row is not None:
            return row.ma_thanh_phan
        return None

    def add_ingredient(self, ingredient_name):
        """Thêm thành phần mới — tự sinh mã TPxx tiếp theo."""
        conn = database_config()
        cursor = conn.cursor()

        # Kiểm tra trùng tên
        cursor.execute("SELECT COUNT(*) FROM ThanhPhan WHERE ten_thanh_phan = ?", (ingredient_name,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False, "Thành phần này đã tồn tại!"

        # Tự sinh mã tiếp theo
        cursor.execute("""
            SELECT TOP 1 ma_thanh_phan FROM ThanhPhan
            ORDER BY CAST(SUBSTRING(ma_thanh_phan, 3, LEN(ma_thanh_phan) - 2) AS INT) DESC
        """)
        row = cursor.fetchone()
        if row:
            last_num = int(row.ma_thanh_phan[2:])
            new_id = f"TP{last_num + 1:02d}"
        else:
            new_id = "TP01"

        cursor.execute(
            "INSERT INTO ThanhPhan (ma_thanh_phan, ten_thanh_phan) VALUES (?, ?)",
            (new_id, ingredient_name)
        )
        conn.commit()
        conn.close()
        return True, f"Đã thêm thành phần '{ingredient_name}' (mã: {new_id})"

    def delete_ingredient(self, ingredient_id):
        """Xóa thành phần theo mã."""
        conn = database_config()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM ThanhPhan WHERE ma_thanh_phan = ?", (ingredient_id,))
        if cursor.fetchone()[0] == 0:
            conn.close()
            return False, "Không tìm thấy thành phần!"

        cursor.execute("DELETE FROM ThanhPhan WHERE ma_thanh_phan = ?", (ingredient_id,))
        conn.commit()
        conn.close()
        return True, "Đã xóa thành phần thành công!"