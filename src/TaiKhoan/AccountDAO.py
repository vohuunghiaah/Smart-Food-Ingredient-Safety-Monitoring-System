import pyodbc
from AccountDTO import AccountDTO

class AccountDAO:
    def get_connection(self):
        return pyodbc.connect(
            r'Driver={ODBC Driver 17 for SQL Server};'
            r'Server=MSI\SQLEXPRESS;'
            r'Database=FOOD;'
            r'Trusted_Connection=yes;'
            r'TrustServerCertificate=yes;'
        )

    def get_account_by_id(self, user_id):
        conn = self.get_connection()
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
        conn = self.get_connection()
        cursor = conn.cursor()


        cursor.execute(
            "INSERT INTO TaiKhoan (ma_nguoi_dung, ten_nguoi_dung, so_dien_thoai, mat_khau) VALUES (?, ?, ?, ?)",
            (account.user_id, account.user_name, account.phone_number, account.password)
        )
        conn.commit()
        conn.close()

    def update_profile_and_allergies(self, account):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE TaiKhoan SET ten_nguoi_dung = ?, so_dien_thoai = ? WHERE ma_nguoi_dung = ?",
            (account.user_name, account.phone_number, account.user_id)
        )


        cursor.execute("DELETE FROM ThanhPhanDiUng WHERE ma_nguoi_dung = ?", (account.user_id,))

        # Add new allergies
        for ingredient_id in account.allergies:
            cursor.execute(
                "INSERT INTO ThanhPhanDiUng (ma_nguoi_dung, ma_thanh_phan) VALUES (?, ?)",
                (account.user_id, ingredient_id)
            )

        conn.commit()
        conn.close()