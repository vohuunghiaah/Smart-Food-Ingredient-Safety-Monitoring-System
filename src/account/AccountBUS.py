import bcrypt
from AccountDAO import AccountDAO
from ingredient.IngredientDAO import IngredientDAO

class AccountBUS:
    def __init__(self):
        self.dao = AccountDAO()
        self.ingredient_dao = IngredientDAO()

    def register(self, account):
        if account.user_id == "" or account.password == "":
            return False, "Không được để trống thông tin!"

        existing_account = self.dao.get_account_by_id(account.user_id)
        if existing_account is not None:
            return False, "Tài khoản đã tồn tại!"

        # Mã hóa mật khẩu bảo mật bằng bcrypt trước khi lưu vào database
        hashed_password = bcrypt.hashpw(account.password.encode('utf-8'), bcrypt.gensalt())
        account.password = hashed_password.decode('utf-8')

        self.dao.add_account(account)
        return True, "Đăng ký thành công!"

    def login(self, user_id, input_password):
        user = self.dao.get_account_by_id(user_id)
        if user is None:
            return False, "Sai mã người dùng!"

        # Lấy mật khẩu đang lưu trong database (hỗ trợ cả thuộc tính mat_khau hoặc password)
        db_password = getattr(user, 'mat_khau', None) or getattr(user, 'password', '')

        if not db_password:
            return False, "Tài khoản không có dữ liệu mật khẩu!"

        # --- Cơ chế kiểm tra mật khẩu thông minh tránh lỗi Invalid salt ---
        try:
            # Trường hợp 1: Nếu mật khẩu trong DB là chuỗi đã mã hóa bcrypt (bắt đầu bằng $2b$ hoặc $2a$)
            if db_password.startswith("$2b$") or db_password.startswith("$2a$"):
                is_match = bcrypt.checkpw(input_password.encode('utf-8'), db_password.encode('utf-8'))
            else:
                # Trường hợp 2: Nếu mật khẩu trong DB là chữ thường/chuỗi thô cũ chưa mã hóa
                is_match = (db_password == input_password)

            if is_match:
                return True, "Đăng nhập thành công!"
            else:
                return False, "Sai mật khẩu!"

        except Exception as e:
            # Phòng hờ mọi lỗi định dạng salt khác, tự động fallback về so sánh text thô
            if db_password == input_password:
                return True, "Đăng nhập thành công!"
            return False, "Sai mật khẩu!"

    def setup_profile(self, user_id, new_name, new_phone, allergy_list):
        user = self.dao.get_account_by_id(user_id)
        if user is None:
            return False, "Không tìm thấy user!"

        user.user_name = new_name
        user.phone_number = new_phone

        allergy_ids = []
        invalid_names = []

        for name in allergy_list:
            name = name.strip()
            ingredient_id = self.ingredient_dao.get_ingredient_id_by_name(name)

            if ingredient_id is not None:
                if ingredient_id not in allergy_ids:
                    allergy_ids.append(ingredient_id)
            else:
                invalid_names.append(name)

        user.allergies = allergy_ids

        self.dao.update_profile_and_allergies(user)

        if len(invalid_names) > 0:
            chuoi_loi = ", ".join(invalid_names)
            return True, f"Lưu thành công! Nhưng các chất không có trong hệ thống:  {chuoi_loi}"

        return True, "Lưu profile thành công!"