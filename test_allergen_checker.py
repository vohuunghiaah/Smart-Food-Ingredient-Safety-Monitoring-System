# ===========================================================================
# File: test_allergen_checker.py
# Muc dich: Kiem tra cac ham tra cuu, so khop thanh phan di ung
#           va phan loai canh bao cua module AllergenChecker
# ===========================================================================

import sys
import os
import io

# Cau hinh encoding UTF-8 cho console Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Them duong dan de import cac module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'allergen_checker'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.allergen_checker.AllergenCheckerBUS import AllergenCheckerBUS

SEP = "=" * 60
SUB = "-" * 60


def test_check_by_barcode():
    """
    Test 1: Kiem tra di ung khi quet ma vach san pham.
    User U01 (Nguyen Van Nam) bi di ung: Sua bo, Dau phong
    San pham SP01 (Sua tuoi Vinamilk) chua: Sua bo
    => Ky vong: Phat hien 1 thanh phan truc tiep -> MEDIUM
    """
    print(f"\n{SEP}")
    print("TEST 1: Kiem tra di ung qua ma vach")
    print(f"  User: U01 (Nguyen Van Nam) - Di ung: Sua bo, Dau phong")
    print(f"  San pham: Ma vach 8934563123456 (Sua tuoi Vinamilk)")
    print(SEP)

    bus = AllergenCheckerBUS()
    result = bus.check_allergens_by_barcode("U01", "8934563123456")
    bus.print_result(result)


def test_check_by_product_id():
    """
    Test 2: Kiem tra di ung theo ma san pham.
    User U01 voi SP02 (Banh Oreo) chua: Sua bo, Ca cao, lua mi
    U01 di ung Sua bo -> Ky vong: MEDIUM (1 truc tiep)
    """
    print(f"\n{SEP}")
    print("TEST 2: Kiem tra di ung theo ma san pham")
    print(f"  User: U01 - San pham: SP02 (Banh Oreo)")
    print(SEP)

    bus = AllergenCheckerBUS()
    result = bus.check_allergens_by_product_id("U01", "SP02")
    bus.print_result(result)


def test_check_safe_product():
    """
    Test 3: Kiem tra san pham AN TOAN cho user.
    User U02 (Le Minh Tien) di ung: lua mi
    San pham SP03 (Nuoc tang luc Sting dau) chua: Dau
    => Ky vong: SAFE
    """
    print(f"\n{SEP}")
    print("TEST 3: Kiem tra san pham AN TOAN")
    print(f"  User: U02 (Le Minh Tien) - Di ung: lua mi")
    print(f"  San pham: SP03 (Nuoc tang luc Sting dau) - chua: Dau")
    print(SEP)

    bus = AllergenCheckerBUS()
    result = bus.check_allergens_by_product_id("U02", "SP03")
    bus.print_result(result)


def test_check_all_products():
    """
    Test 4: Kiem tra TOAN BO san pham cho 1 user.
    User U01 - Kiem tra tat ca 4 san pham trong he thong.
    Ket qua sap xep theo muc canh bao giam dan.
    """
    print(f"\n{SEP}")
    print("TEST 4: Kiem tra TOAN BO san pham cho User U01")
    print(SEP)

    bus = AllergenCheckerBUS()
    results = bus.check_all_products_for_user("U01")

    print(f"\n  Tong so san pham: {len(results)}")
    print(f"  Sap xep theo muc canh bao giam dan:\n")

    for i, r in enumerate(results, 1):
        matched_names = ", ".join(m["name"] for m in r.matched_allergens) if r.matched_allergens else "Khong co"
        print(f"  {i}. [{r.warning_level:<8}] {r.product_name:<40} | Di ung: {matched_names}")

    # In chi tiet tung ket qua
    for r in results:
        bus.print_result(r)


def test_nonexistent_product():
    """
    Test 5: Kiem tra san pham khong ton tai.
    """
    print(f"\n{SEP}")
    print("TEST 5: Kiem tra san pham KHONG TON TAI")
    print(SEP)

    bus = AllergenCheckerBUS()
    result = bus.check_allergens_by_barcode("U01", "0000000000000")
    print(f"  Ket qua: {result.warning_message}")


# ===========================================================================
# CHAY TAT CA CAC TEST
# ===========================================================================
if __name__ == "__main__":
    print(SEP)
    print("  ALLERGEN CHECKER - KIEM TRA HE THONG")
    print(SEP)

    try:
        test_check_by_barcode()       # Test 1: So khop qua ma vach
        test_check_by_product_id()    # Test 2: So khop qua ma san pham
        test_check_safe_product()     # Test 3: San pham an toan
        test_check_all_products()     # Test 4: Kiem tra toan bo
        test_nonexistent_product()    # Test 5: San pham khong ton tai

        print(f"\n{SEP}")
        print("  TAT CA CAC TEST DA HOAN THANH!")
        print(SEP)

    except Exception as e:
        print(f"\n[LOI] {e}")
        import traceback
        traceback.print_exc()
