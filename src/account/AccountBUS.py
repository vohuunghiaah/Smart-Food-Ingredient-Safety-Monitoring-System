import re
import bcrypt
from account.AccountDAO import AccountDAO
from account.AccountDTO import AccountDTO
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
    
    
    def login_by_phone(self, phone_number, input_password):
        # Lấy user theo SĐT
        user = self.dao.get_account_by_phone(phone_number)
        if user is None:
            # Trả về False, Thông báo lỗi, và None cho user_id
            return False, "Sai tài khoản hoặc mật khẩu!", None

        db_password = getattr(user, 'mat_khau', None) or getattr(user, 'password', '')

        if not db_password:
            return False, "Tài khoản không có dữ liệu mật khẩu!", None

        try:
            if db_password.startswith("$2b$") or db_password.startswith("$2a$"):
                is_match = bcrypt.checkpw(input_password.encode('utf-8'), db_password.encode('utf-8'))
            else:
                is_match = (db_password == input_password)

            if is_match:
                # Đăng nhập thành công, trả về kèm user.user_id để main.py lấy đi query sản phẩm
                return True, "Đăng nhập thành công!", user.user_id
            else:
                return False, "Sai tài khoản hoặc mật khẩu!", None

        except Exception as e:
            if db_password == input_password:
                return True, "Đăng nhập thành công!", user.user_id
            return False, "Sai tài khoản hoặc mật khẩu!", None

    # ===================================================================
    # CÁC PHƯƠNG THỨC MỚI CHO WEB APP
    # ===================================================================

    def register_by_phone(self, user_name, phone_number, password):
        """
        Đăng ký tài khoản mới bằng số điện thoại.
        Validate đầu vào, hash password, tự sinh mã user.
        """
        # Validate tên
        if not user_name or len(user_name.strip()) < 2:
            return False, "Họ tên phải có ít nhất 2 ký tự!"

        # Validate SĐT: 10 số, bắt đầu bằng 0
        phone_number = phone_number.strip()
        if not re.match(r'^0\d{9}$', phone_number):
            return False, "Số điện thoại không hợp lệ! (10 số, bắt đầu bằng 0)"

        # Validate mật khẩu
        if not password or len(password) < 6:
            return False, "Mật khẩu phải có ít nhất 6 ký tự!"

        # Kiểm tra SĐT đã tồn tại
        if self.dao.phone_exists(phone_number):
            return False, "Số điện thoại này đã được đăng ký!"

        # Tự sinh mã user
        new_user_id = self.dao.generate_next_user_id()

        # Hash mật khẩu
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Tạo DTO và lưu
        account = AccountDTO(
            user_id=new_user_id,
            user_name=user_name.strip(),
            phone_number=phone_number,
            password=hashed_password.decode('utf-8')
        )
        self.dao.add_account(account)

        return True, "Đăng ký thành công! Vui lòng đăng nhập."

    def get_user_profile(self, user_id):
        """
        Lấy thông tin profile của user bao gồm tên các chất dị ứng.
        Trả về dict chứa thông tin user + danh sách tên chất dị ứng.
        """
        user = self.dao.get_account_by_id(user_id)
        if user is None:
            return None

        # Lấy tên thành phần dị ứng từ mã
        allergy_names = []
        all_ingredients = self.ingredient_dao.get_all_ingredients()
        ingredient_map = {ing.ingredient_id: ing.ingredient_name for ing in all_ingredients}

        for allergy_id in user.allergies:
            name = ingredient_map.get(allergy_id, allergy_id)
            allergy_names.append(name)

        return {
            "user_id": user.user_id,
            "user_name": user.user_name,
            "phone_number": user.phone_number,
            "allergies": allergy_names,
            "allergy_ids": user.allergies
        }

    def update_profile_web(self, user_id, new_name, allergy_names_list):
        """
        Cập nhật hồ sơ từ web (không đổi SĐT, chỉ đổi tên + dị ứng).
        allergy_names_list: list các tên thành phần dị ứng.
        """
        user = self.dao.get_account_by_id(user_id)
        if user is None:
            return False, "Không tìm thấy tài khoản!"

        # Cập nhật tên
        if new_name and len(new_name.strip()) >= 2:
            user.user_name = new_name.strip()

        # Chuyển tên thành phần → mã thành phần
        allergy_ids = []
        invalid_names = []

        for name in allergy_names_list:
            name = name.strip()
            if not name:
                continue
            ingredient_id = self.ingredient_dao.get_ingredient_id_by_name(name)
            if ingredient_id is not None:
                if ingredient_id not in allergy_ids:
                    allergy_ids.append(ingredient_id)
            else:
                invalid_names.append(name)

        user.allergies = allergy_ids
        self.dao.update_profile_and_allergies(user)

        if invalid_names:
            return True, f"Đã lưu! Nhưng không tìm thấy: {', '.join(invalid_names)}"

        return True, "Cập nhật hồ sơ thành công!"