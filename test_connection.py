# ===========================================================================
# File: test_connection.py
# Muc dich: Kiem tra ket noi toi SQL Server va truy van du lieu mau
#           tu co so du lieu FOOD (He thong Giam sat An toan Thuc pham)
# ===========================================================================

import sys
import io

# ---- Cau hinh encoding UTF-8 cho console Windows ----
# Tranh loi UnicodeEncodeError khi in tieng Viet tren Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from utils import database_config

# ------- Dinh dang hien thi tren console -------
SEPARATOR = "=" * 60
SUB_SEPARATOR = "-" * 60


def test_query_san_pham(cursor):
    """
    Truy van danh sach san pham cung ten nhom san pham.
    JOIN bang SanPham voi NhomSanPham de lay ten nhom.
    """
    print(f"\n{SUB_SEPARATOR}")
    print("[*] DANH SACH SAN PHAM (SanPham JOIN NhomSanPham)")
    print(SUB_SEPARATOR)

    query = """
        SELECT sp.ma_san_pham, sp.ma_vach, sp.ten_san_pham, nsp.ten_nhom
        FROM SanPham sp
        LEFT JOIN NhomSanPham nsp ON sp.ma_nhom_san_pham = nsp.ma_nhom
        ORDER BY sp.ma_san_pham
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    if rows:
        # In header bang
        print(f"{'Ma SP':<10} {'Ma vach':<16} {'Ten san pham':<40} {'Nhom SP'}")
        print("-" * 90)
        for row in rows:
            print(f"{row[0]:<10} {row[1]:<16} {row[2]:<40} {row[3]}")
    else:
        print("  (Khong co du lieu)")

    print(f"  -> Tong cong: {len(rows)} san pham")


def test_query_thanh_phan(cursor):
    """
    Truy van danh sach thanh phan kem cac ten goi khac (neu co).
    JOIN bang ThanhPhan voi TenGoiKhac.
    """
    print(f"\n{SUB_SEPARATOR}")
    print("[*] DANH SACH THANH PHAN VA TEN GOI KHAC (ThanhPhan JOIN TenGoiKhac)")
    print(SUB_SEPARATOR)

    query = """
        SELECT tp.ma_thanh_phan, tp.ten_thanh_phan, tgk.ten_goi_khac
        FROM ThanhPhan tp
        LEFT JOIN TenGoiKhac tgk ON tp.ma_thanh_phan = tgk.ma_thanh_phan
        ORDER BY tp.ma_thanh_phan
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    if rows:
        print(f"{'Ma TP':<10} {'Ten thanh phan':<30} {'Ten goi khac'}")
        print("-" * 70)
        for row in rows:
            ten_goi_khac = row[2] if row[2] else "(khong co)"
            print(f"{row[0]:<10} {row[1]:<30} {ten_goi_khac}")
    else:
        print("  (Khong co du lieu)")


def test_query_thanh_phan_san_pham(cursor):
    """
    Truy van thanh phan cua tung san pham.
    JOIN 3 bang: SanPham, ThanhPhanSanPham, ThanhPhan.
    """
    print(f"\n{SUB_SEPARATOR}")
    print("[*] THANH PHAN CUA TUNG SAN PHAM (SanPham <-> ThanhPhan)")
    print(SUB_SEPARATOR)

    query = """
        SELECT sp.ten_san_pham, tp.ten_thanh_phan
        FROM ThanhPhanSanPham tpsp
        INNER JOIN SanPham sp ON tpsp.ma_san_pham = sp.ma_san_pham
        INNER JOIN ThanhPhan tp ON tpsp.ma_thanh_phan = tp.ma_thanh_phan
        ORDER BY sp.ten_san_pham, tp.ten_thanh_phan
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    if rows:
        print(f"{'Ten san pham':<45} {'Thanh phan'}")
        print("-" * 75)
        for row in rows:
            print(f"{row[0]:<45} {row[1]}")
    else:
        print("  (Khong co du lieu)")


def test_query_di_ung_user(cursor):
    """
    Truy van danh sach nguoi dung va cac thanh phan di ung cua ho.
    JOIN 3 bang: TaiKhoan, ThanhPhanDiUng, ThanhPhan.
    """
    print(f"\n{SUB_SEPARATOR}")
    print("[!] THANH PHAN DI UNG CUA NGUOI DUNG (TaiKhoan <-> ThanhPhan)")
    print(SUB_SEPARATOR)

    query = """
        SELECT tk.ten_nguoi_dung, tk.so_dien_thoai, tp.ten_thanh_phan
        FROM ThanhPhanDiUng tpdu
        INNER JOIN TaiKhoan tk ON tpdu.ma_nguoi_dung = tk.ma_nguoi_dung
        INNER JOIN ThanhPhan tp ON tpdu.ma_thanh_phan = tp.ma_thanh_phan
        ORDER BY tk.ten_nguoi_dung
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    if rows:
        print(f"{'Ten nguoi dung':<25} {'SDT':<15} {'Thanh phan di ung'}")
        print("-" * 65)
        for row in rows:
            print(f"{row[0]:<25} {row[1]:<15} {row[2]}")
    else:
        print("  (Khong co du lieu)")


def test_query_thong_ke(cursor):
    """
    Thong ke tong quan: dem so luong ban ghi trong moi bang.
    """
    print(f"\n{SUB_SEPARATOR}")
    print("[*] THONG KE TONG QUAN")
    print(SUB_SEPARATOR)

    # Danh sach cac bang can dem
    tables = [
        ("NhomSanPham", "Nhom san pham"),
        ("SanPham", "San pham"),
        ("ThanhPhan", "Thanh phan"),
        ("TaiKhoan", "Tai khoan"),
        ("TenGoiKhac", "Ten goi khac"),
        ("ThanhPhanDiUng", "Thanh phan di ung"),
        ("ThanhPhanSanPham", "Thanh phan san pham"),
    ]

    for table_name, display_name in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  - {display_name:<25} ({table_name}): {count} ban ghi")


# ===========================================================================
# CHUONG TRINH CHINH
# ===========================================================================
if __name__ == "__main__":
    print(SEPARATOR)
    print("[*] KIEM TRA KET NOI SQL SERVER")
    print(SEPARATOR)

    try:
        # ---- Buoc 1: Thu ket noi toi SQL Server ----
        conn = database_config.get_connection()
        print("[THANH CONG] Python da ket noi duoc voi SQL Server!")
        print(f"   Server info: {conn.getinfo(17)}")  # SQL_DBMS_NAME

        # Tao cursor de thuc thi truy van
        cursor = conn.cursor()

        # ---- Buoc 2: Kiem tra phien ban SQL Server ----
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        print(f"   SQL Server version: {version.split(chr(10))[0]}")  # Lay dong dau

        # ---- Buoc 3: Truy van du lieu tu cac bang ----
        print(f"\n{SEPARATOR}")
        print("[*] TRUY VAN DU LIEU MAU TU CO SO DU LIEU")
        print(SEPARATOR)

        # Thong ke tong quan
        test_query_thong_ke(cursor)

        # Danh sach san pham
        test_query_san_pham(cursor)

        # Danh sach thanh phan va ten goi khac
        test_query_thanh_phan(cursor)

        # Thanh phan cua tung san pham
        test_query_thanh_phan_san_pham(cursor)

        # Thanh phan di ung cua nguoi dung
        test_query_di_ung_user(cursor)

        # ---- Buoc 4: Dong ket noi ----
        print(f"\n{SEPARATOR}")
        cursor.close()
        conn.close()
        print("[OK] Da dong ket noi SQL Server thanh cong.")
        print(SEPARATOR)

    except Exception as e:
        # Neu ket noi that bai, in thong bao loi chi tiet
        print(f"\n[THAT BAI] Loi ket noi SQL Server!")
        print(f"   Chi tiet loi: {e}")
        print(f"\n[GOI Y] Khac phuc:")
        print(f"   1. Kiem tra SQL Server da duoc khoi dong chua")
        print(f"   2. Kiem tra ten server trong file parameter.env")
        print(f"   3. Kiem tra da cai ODBC Driver 17 for SQL Server chua")
        print(f"   4. Kiem tra database FOOD da duoc tao chua")
        print(SEPARATOR)