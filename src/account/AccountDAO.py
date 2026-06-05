
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