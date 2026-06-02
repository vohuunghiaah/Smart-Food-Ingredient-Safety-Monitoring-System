import sys
import os

# Them duong dan goc cua project vao sys.path de import utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from utils.database_config import database_config


class AllergenCheckerDAO:
    """
    DAO chiu trach nhiem truy van du lieu lien quan den:
    - Thanh phan san pham (ThanhPhanSanPham)
    - Thanh phan di ung cua nguoi dung (ThanhPhanDiUng)
    - Ten goi khac cua thanh phan (TenGoiKhac)
    - Thong tin san pham (SanPham, NhomSanPham)
    """

    def get_product_by_barcode(self, barcode):
        """
        Tra cuu san pham theo ma vach.
        Tra ve dict {"id", "name", "group"} hoac None neu khong tim thay.
        """
        conn = database_config()
        cursor = conn.cursor()

        query = """
            SELECT sp.ma_san_pham, sp.ten_san_pham, nsp.ten_nhom
            FROM SanPham sp
            LEFT JOIN NhomSanPham nsp ON sp.ma_nhom_san_pham = nsp.ma_nhom
            WHERE sp.ma_vach = ?
        """
        cursor.execute(query, (barcode,))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        return {
            "id": row[0],
            "name": row[1],
            "group": row[2]
        }

    def get_product_by_id(self, product_id):
        """
        Tra cuu san pham theo ma san pham.
        Tra ve dict {"id", "name", "group"} hoac None neu khong tim thay.
        """
        conn = database_config()
        cursor = conn.cursor()

        query = """
            SELECT sp.ma_san_pham, sp.ten_san_pham, nsp.ten_nhom
            FROM SanPham sp
            LEFT JOIN NhomSanPham nsp ON sp.ma_nhom_san_pham = nsp.ma_nhom
            WHERE sp.ma_san_pham = ?
        """
        cursor.execute(query, (product_id,))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        return {
            "id": row[0],
            "name": row[1],
            "group": row[2]
        }

    def get_product_ingredients(self, product_id):
        """
        Lay danh sach tat ca thanh phan cua mot san pham.
        Tra ve list [{"id", "name"}]
        """
        conn = database_config()
        cursor = conn.cursor()

        query = """
            SELECT tp.ma_thanh_phan, tp.ten_thanh_phan
            FROM ThanhPhanSanPham tpsp
            INNER JOIN ThanhPhan tp ON tpsp.ma_thanh_phan = tp.ma_thanh_phan
            WHERE tpsp.ma_san_pham = ?
            ORDER BY tp.ten_thanh_phan
        """
        cursor.execute(query, (product_id,))
        rows = cursor.fetchall()
        conn.close()

        return [{"id": row[0], "name": row[1]} for row in rows]

    def get_ingredient_aliases(self, ingredient_id):
        """
        Lay danh sach ten goi khac cua mot thanh phan.
        Tra ve list ["ten_goi_khac_1", "ten_goi_khac_2", ...]
        """
        conn = database_config()
        cursor = conn.cursor()

        query = """
            SELECT ten_goi_khac
            FROM TenGoiKhac
            WHERE ma_thanh_phan = ?
        """
        cursor.execute(query, (ingredient_id,))
        rows = cursor.fetchall()
        conn.close()

        return [row[0] for row in rows]

    def get_user_allergies(self, user_id):
        """
        Lay danh sach thanh phan di ung cua nguoi dung.
        Tra ve list [{"id", "name"}]
        """
        conn = database_config()
        cursor = conn.cursor()

        query = """
            SELECT tp.ma_thanh_phan, tp.ten_thanh_phan
            FROM ThanhPhanDiUng tpdu
            INNER JOIN ThanhPhan tp ON tpdu.ma_thanh_phan = tp.ma_thanh_phan
            WHERE tpdu.ma_nguoi_dung = ?
            ORDER BY tp.ten_thanh_phan
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        conn.close()

        return [{"id": row[0], "name": row[1]} for row in rows]

    def get_all_products(self):
        """
        Lay danh sach tat ca san pham.
        Tra ve list [{"id", "name", "barcode", "group"}]
        """
        conn = database_config()
        cursor = conn.cursor()

        query = """
            SELECT sp.ma_san_pham, sp.ma_vach, sp.ten_san_pham, nsp.ten_nhom
            FROM SanPham sp
            LEFT JOIN NhomSanPham nsp ON sp.ma_nhom_san_pham = nsp.ma_nhom
            ORDER BY sp.ma_san_pham
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        return [{"id": row[0], "barcode": row[1], "name": row[2], "group": row[3]} for row in rows]
