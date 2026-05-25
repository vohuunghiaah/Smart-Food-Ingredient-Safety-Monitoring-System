import pyodbc
from TaiKhoanDTO import TaiKhoanDTO

class TaiKhoanDAO:
    def get_connection(self):

        return pyodbc.connect(
            r'Driver={ODBC Driver 17 for SQL Server};'
            r'Server=MSI\SQLEXPRESS;'
            r'Database=FOOD;'
            r'Trusted_Connection=yes;'
            r'TrustServerCertificate=yes;'
        )

    def lay_tai_khoan_theo_ma(self, ma_nguoi_dung):
        conn = self.get_connection()
        cursor = conn.cursor()


        cursor.execute("SELECT * FROM TaiKhoan WHERE ma_nguoi_dung = ?", (ma_nguoi_dung,))
        row = cursor.fetchone()

        if row == None:
            conn.close()
            return None


        tk = TaiKhoanDTO(row.ma_nguoi_dung, row.ten_nguoi_dung, row.so_dien_thoai, row.mat_khau)


        cursor.execute("SELECT ma_thanh_phan FROM ThanhPhanDiUng WHERE ma_nguoi_dung = ?", (ma_nguoi_dung,))
        di_ung_rows = cursor.fetchall()


        for d in di_ung_rows:
            tk.danh_sach_di_ung.append(d.ma_thanh_phan)

        conn.close()
        return tk

    def them_tai_khoan(self, tk):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO TaiKhoan (ma_nguoi_dung, ten_nguoi_dung, so_dien_thoai, mat_khau) VALUES (?, ?, ?, ?)",
            (tk.ma_nguoi_dung, tk.ten_nguoi_dung, tk.so_dien_thoai, tk.mat_khau)
        )
        conn.commit()
        conn.close()

    def cap_nhat_profile_va_di_ung(self, tk):
        conn = self.get_connection()
        cursor = conn.cursor()


        cursor.execute(
            "UPDATE TaiKhoan SET ten_nguoi_dung = ?, so_dien_thoai = ? WHERE ma_nguoi_dung = ?",
            (tk.ten_nguoi_dung, tk.so_dien_thoai, tk.ma_nguoi_dung)
        )

        # xoa
        cursor.execute("DELETE FROM ThanhPhanDiUng WHERE ma_nguoi_dung = ?", (tk.ma_nguoi_dung,))

        # them
        for ma_tp in tk.danh_sach_di_ung:
            cursor.execute(
                "INSERT INTO ThanhPhanDiUng (ma_nguoi_dung, ma_thanh_phan) VALUES (?, ?)",
                (tk.ma_nguoi_dung, ma_tp)
            )

        conn.commit()
        conn.close()