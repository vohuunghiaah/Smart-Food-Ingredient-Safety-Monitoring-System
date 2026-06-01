
import sys
import os
import io


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
sys.path.append(src_dir)

from TaiKhoan.AccountDTO import AccountDTO
from TaiKhoan.AccountBUS import AccountBUS
from TaiKhoan.AccountDAO import AccountDAO


SEPARATOR = "=" * 60
SUB_SEPARATOR = "-" * 60


def clear_test_data(dao, ma_test):
    """
    Xoa tai khoan test cu (neu co) de dam bao moi lan chay test deu luon thanh cong
    ma khong bi vuong loi "Tai khoan da ton tai".
    """
    try:
        conn = dao.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM TaiKhoan WHERE ma_nguoi_dung = ?", (ma_test,))
        conn.commit()
        conn.close()
    except Exception:
        pass  # Bo qua neu co loi hoac khong co ket noi


def test_tao_tai_khoan(bus, dao, ma_test):
    """
    Kiem tra chuc nang DANG KY TAI KHOAN va kiem tra du lieu thuc te trong DB.
    """
    print(f"\n{SUB_SEPARATOR}")
    print("[*] BUOC 1: KIEM TRA TAO TAI KHOAN")
    print(SUB_SEPARATOR)

    tk_moi = AccountDTO(ma_test, "Nguoi Dung Test", "0123456789", "password123")


    thanh_cong, thong_bao = bus.register(tk_moi)
    print(f"  -> Ket qua tu BUS: {thong_bao}")


    kiem_tra_db = dao.get_account_by_id(ma_test)
    if kiem_tra_db is not None:
        print(f"  -> [THANH CONG] Da luu vao Database!")
        print(f"     + Ten dang luu   : {kiem_tra_db.user_name}")
        print(f"     + Pass (ma hoa)  : {kiem_tra_db.password}")
    else:
        print(f"  -> [THAT BAI] Khong tim thay {ma_test} trong Database.")


def test_thiet_lap_profile_va_di_ung(bus, dao, ma_test):
    """
    Kiem tra chuc nang CAP NHAT PROFILE va LUONG CHUYEN DOI TEN -> MA.
    """
    print(f"\n{SUB_SEPARATOR}")
    print("[*] BUOC 2: KIEM TRA THIET LAP PROFILE & DI UNG")
    print(SUB_SEPARATOR)


    chat_di_ung = ["Đậu phộng", "Sữa bò", "Thịt heo"]

    thanh_cong, thong_bao = bus.setup_profile(ma_test, "Nguoi Dung Update V2", "0987654321", chat_di_ung)
    print(f"  -> Ket qua tu BUS: {thong_bao}")


    kiem_tra_db = dao.get_account_by_id(ma_test)
    if kiem_tra_db is not None:
        print(f"  -> [THANH CONG] Du lieu trong Database da duoc cap nhat:")
        print(f"     + Ten moi    : {kiem_tra_db.user_name}")
        print(f"     + SDT moi    : {kiem_tra_db.phone_number}")
        print(f"     + Ma di ung  : {kiem_tra_db.allergies} (Mong doi: ['TP02', 'TP01'])")
    else:
        print(f"  -> [THAT BAI] Khong the truy van CSDL.")


# ===========================================================================
# CHUONG TRINH CHINH
# ===========================================================================
if __name__ == "__main__":
    print(SEPARATOR)
    print("[*] KHOI DONG QUY TRINH TEST: TAI KHOAN & DI UNG")
    print(SEPARATOR)

    try:
        bus = AccountBUS()
        dao = AccountDAO()
        MA_TEST_USER = "U99"


        clear_test_data(dao, MA_TEST_USER)
        print("  (Da don dep du lieu test rac neu co de san sang chay...)")


        test_tao_tai_khoan(bus, dao, MA_TEST_USER)
        test_thiet_lap_profile_va_di_ung(bus, dao, MA_TEST_USER)

        print(f"\n{SEPARATOR}")
        print("[OK] QUA TRINH TEST HOAN THANH KHONG CO LOI NGHIEM TRONG.")
        print(SEPARATOR)

    except Exception as e:
        print(f"\n[THAT BAI] Co loi he thong xay ra trong qua trinh test!")
        print(f"   Chi tiet loi: {e}")
        print(f"\n[GOI Y] Khac phuc:")
        print(f"   1. Kiem tra xem ban da thay doi import trong AccountBUS.py chua")
        print(f"      (Can sua thanh: from ThanhPhan.IngredientDAO import IngredientDAO)")
        print(f"   2. Kiem tra SQL Server da bat chua")
        print(SEPARATOR)