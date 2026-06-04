import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
# Import
from account.AccountBUS import AccountBUS
from allergen_checker.AllergenCheckerBUS import AllergenCheckerBUS
from scanner.scanner import get_product_from_openfoodfacts

class MainApplication:
    def __init__(self):
        self.account_bus = AccountBUS()
        self.allergen_bus = AllergenCheckerBUS()
        self.current_user_id = None

    def execute_login(self):
        print("      HỆ THỐNG CẢNH BÁO DỊ ỨNG THỰC PHẨM")
        print("=" * 50)
        print("Vui lòng đăng nhập hệ thống để tiếp tục.")

        user_id = input("Mã người dùng (User ID): ").strip()
        password = input("Mật khẩu: ").strip()

        # Gọi file AccountBUS xử lý kiểm tra tài khoản từ SQL Server
        success, message = self.account_bus.login(user_id, password)
        print(f">> {message}")

        if success:
            self.current_user_id = user_id
            # Gọi tầng DAO để lấy thông tin hiển thị lời chào
            user_info = self.account_bus.dao.get_account_by_id(user_id)
            print(f"Chào mừng quay trở lại, {user_info.user_name}!")
            return True

        return False

    def run_check_flow(self, barcode):
        """Điều phối kiểm tra dị ứng giữa SQL nội bộ và API Cloud"""
        print(f"\n[+] ĐANG TIẾN HÀNH KIỂM TRA MÀ VẠCH: {barcode}")

        # Gọi AllergenCheckerBUS xử lý so khớp chất dị ứng gốc + tên gọi khác (alias)
        result = self.allergen_bus.check_allergens_by_barcode(self.current_user_id, barcode)

        # Trường hợp 1: Có sẵn sản phẩm trong SQL Server của hệ thống
        if result.product_name is not None:
            # Gọi hàm hiển thị kết quả format đẹp mắt có sẵn trong file BUS của bạn
            self.allergen_bus.print_result(result)

        # Trường hợp 2: Không có ở local -> Chuyển tiếp truy vấn sang OpenFoodFacts
        else:
            print("\n[!] Không tìm thấy sản phẩm này trong Database nội bộ.")
            print("[*] Đang kết nối API OpenFoodFacts trực tuyến...")

            food = get_product_from_openfoodfacts(barcode)
            if food:
                print("\n" + "=" * 25 + " KẾT QUẢ TỪ CLOUD " + "=" * 25)
                print(f"  Sản phẩm  : {food['name']}")
                print(f"  Phân nhóm : {food['category']}")
                print("-" * 60)

                # Gọi DAO của AllergenChecker lấy list dị ứng của user hiện tại để đối chiếu thủ công với API
                user_allergies = self.allergen_bus.dao.get_user_allergies(self.current_user_id)
                matched_online = []

                if food["ingredients"]:
                    print("  Thành phần phân tích từ Cloud:")
                    for ing_name in food["ingredients"]:
                        print(f"    - {ing_name}")
                        for allergy in user_allergies:
                            if allergy["name"].lower() in ing_name.lower():
                                matched_online.append(allergy["name"])
                else:
                    print("    (Không lấy được dữ liệu thành phần trực tuyến)")

                print("-" * 60)
                if matched_online:
                    print(f"  [XXXX] MỨC CẢNH BÁO: CRITICAL")
                    print(
                        f"  NGUY HIỂM: Phát hiện chất dị ứng trùng với bạn: {', '.join(set(matched_online))}. KHÔNG NÊN SỬ DỤNG!")
                else:
                    print(f"  [OK] MỨC CẢNH BÁO: SAFE")
                    print("  AN TOÀN: Sản phẩm online không chứa thành phần dị ứng của bạn.")
                print("=" * 68)
            else:
                print("[X] Mã vạch này không tồn tại trên hệ thống dữ liệu OpenFoodFacts.")

    def start(self):
        # Bước 1: Yêu cầu đăng nhập trước
        if not self.execute_login():
            print("Đăng nhập thất bại. Đóng chương trình!")
            return

        # Bước 2: Chuyển sang Menu điều khiển chính sau khi đăng nhập thành công
        while True:
            print("\n" + "~" * 42)
            print("  1. BẬT CAMERA QUÉT MÃ VẠCH SẢN PHẨM")
            print("  2. ĐĂNG XUẤT & THOÁT")
            print("~" * 42)
            choice = input("Nhập lựa chọn của bạn: ").strip()

            if choice == "1":
                # Nhập trực tiếp hàm main() quét camera từ file gốc scanner.py của Tiên
                from scanner import scanner

                print("\n[HỆ THỐNG] Kích hoạt Camera từ file scanner.py...")
                # Thay vì tự code camera, chạy hàm quét của file scanner và lấy mã vạch trả về
                barcode = scanner.scan_barcode_from_camera()

                if barcode:
                    self.run_check_flow(barcode)
                else:
                    print("\n[HỆ THỐNG] Đã hủy quét hoặc không nhận diện được mã vạch.")
            elif choice == "2":
                print("\nđăng xuất tài khoản")
                break
            else:
                print("[!] Lựa chọn không hợp lệ, vui lòng chọn lại.")


if __name__ == "__main__":
    app = MainApplication()
    app.start()