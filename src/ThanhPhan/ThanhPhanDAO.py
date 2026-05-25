import pyodbc
from ThanhPhanDTO import ThanhPhanDTO

class ThanhPhanDAO:
    def get_connection(self):

        return pyodbc.connect(
            r'Driver={ODBC Driver 17 for SQL Server};'
            r'Server=MSI\SQLEXPRESS;'
            r'Database=FOOD;'
            r'Trusted_Connection=yes;'
            r'TrustServerCertificate=yes;'
        )

    def lay_tat_ca_thanh_phan(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT ma_thanh_phan, ten_thanh_phan FROM ThanhPhan")
        rows = cursor.fetchall()

        danh_sach = []
        for row in rows:
            tp = ThanhPhanDTO(row.ma_thanh_phan, row.ten_thanh_phan)
            danh_sach.append(tp)

        conn.close()
        return danh_sach