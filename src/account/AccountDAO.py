
from account.AccountDTO import AccountDTO
from utils.database_config import database_config
class AccountDAO:
    def get_account_by_id(self, user_id):
        # Gọi thẳng từ module database_config, không dùng self
        conn = database_config()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM TaiKhoan WHERE ma_nguoi_dung = ?", (user_id,))
        row = cursor.fetchone()

        if row is None:
            conn.close()
            return None

        account = AccountDTO(row.ma_nguoi_dung, row.ten_nguoi_dung, row.so_dien_thoai, row.mat_khau)

        cursor.execute("SELECT ma_thanh_phan FROM ThanhPhanDiUng WHERE ma_nguoi_dung = ?", (user_id,))
        allergy_rows = cursor.fetchall()

        for allergy in allergy_rows:
            account.allergies.append(allergy.ma_thanh_phan)

        conn.close()
        return account

    def add_account(self, account):
        conn = database_config()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO TaiKhoan (ma_nguoi_dung, ten_nguoi_dung, so_dien_thoai, mat_khau) VALUES (?, ?, ?, ?)",
            (account.user_id, account.user_name, account.phone_number, account.password)
        )
        conn.commit()
        conn.close()

    def update_profile_and_allergies(self, account):
        conn = database_config()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE TaiKhoan SET ten_nguoi_dung = ?, so_dien_thoai = ? WHERE ma_nguoi_dung = ?",
            (account.user_name, account.phone_number, account.user_id)
        )

        cursor.execute("DELETE FROM ThanhPhanDiUng WHERE ma_nguoi_dung = ?", (account.user_id,))


        for ingredient_id in account.allergies:
            cursor.execute(
                "INSERT INTO ThanhPhanDiUng (ma_nguoi_dung, ma_thanh_phan) VALUES (?, ?)",
                (account.user_id, ingredient_id)
            )

        conn.commit()
        conn.close()
    
    def get_account_by_phone(self, phone_number):
        conn = database_config()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM TaiKhoan WHERE so_dien_thoai = ?", (phone_number,))
        row = cursor.fetchone()

        if row is None:
            conn.close()
            return None

        account = AccountDTO(row.ma_nguoi_dung, row.ten_nguoi_dung, row.so_dien_thoai, row.mat_khau)

        cursor.execute("SELECT ma_thanh_phan FROM ThanhPhanDiUng WHERE ma_nguoi_dung = ?", (row.ma_nguoi_dung,))
        allergy_rows = cursor.fetchall()

        for allergy in allergy_rows:
            account.allergies.append(allergy.ma_thanh_phan)

        conn.close()
        return account

    def phone_exists(self, phone_number):
        """Kiểm tra số điện thoại đã được đăng ký chưa."""
        conn = database_config()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM TaiKhoan WHERE so_dien_thoai = ?", (phone_number,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def generate_next_user_id(self):
        """Tự sinh mã người dùng tiếp theo (U01, U02, ...)."""
        conn = database_config()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TOP 1 ma_nguoi_dung FROM TaiKhoan 
            ORDER BY CAST(SUBSTRING(ma_nguoi_dung, 2, LEN(ma_nguoi_dung) - 1) AS INT) DESC
        """)
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return "U01"
        
        # Lấy số cuối cùng, +1
        last_num = int(row.ma_nguoi_dung[1:])
        next_num = last_num + 1
        return f"U{next_num:02d}"

    def update_password(self, user_id, new_hashed_password):
        """Cập nhật mật khẩu đã hash cho user."""
        conn = database_config()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE TaiKhoan SET mat_khau = ? WHERE ma_nguoi_dung = ?",
            (new_hashed_password, user_id)
        )
        conn.commit()
        conn.close()