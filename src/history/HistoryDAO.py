import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from utils.database_config import database_config


class HistoryDAO:
    """
    DAO quản lý lịch sử quét sản phẩm.
    Lưu và truy vấn bảng LichSuQuet.
    """

    def add_scan_record(self, user_id, barcode, product_name, warning_level):
        """
        Thêm một bản ghi lịch sử quét mới.
        
        Params:
            user_id       : Mã người dùng (VD: 'U01')
            barcode       : Mã vạch sản phẩm
            product_name  : Tên sản phẩm
            warning_level : Mức cảnh báo (SAFE/LOW/MEDIUM/HIGH/CRITICAL)
        """
        try:
            conn = database_config()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO LichSuQuet (ma_nguoi_dung, ma_vach, ten_san_pham, muc_canh_bao)
                   VALUES (?, ?, ?, ?)""",
                (user_id, barcode, product_name, warning_level)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            # Bảng LichSuQuet có thể chưa được tạo — không crash app
            print(f"[HistoryDAO] Lỗi khi lưu lịch sử: {e}")

    def get_user_history(self, user_id, limit=20):
        """
        Lấy lịch sử quét gần nhất của user.
        
        Params:
            user_id : Mã người dùng
            limit   : Số lượng bản ghi tối đa (mặc định 20)
            
        Returns:
            list[dict] — [{id, barcode, product_name, warning_level, scan_time}]
        """
        try:
            conn = database_config()
            cursor = conn.cursor()
            cursor.execute(
                """SELECT TOP (?) id, ma_vach, ten_san_pham, muc_canh_bao, thoi_gian
                   FROM LichSuQuet
                   WHERE ma_nguoi_dung = ?
                   ORDER BY thoi_gian DESC""",
                (limit, user_id)
            )
            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    "id": row[0],
                    "barcode": row[1],
                    "product_name": row[2],
                    "warning_level": row[3],
                    "scan_time": row[4].strftime("%d/%m/%Y %H:%M") if row[4] else ""
                }
                for row in rows
            ]
        except Exception as e:
            print(f"[HistoryDAO] Lỗi khi đọc lịch sử: {e}")
            return []
