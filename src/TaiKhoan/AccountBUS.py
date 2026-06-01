import bcrypt
from AccountDAO import AccountDAO
from ThanhPhan.IngredientDAO import IngredientDAO


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

        hashed_password = bcrypt.hashpw(account.password.encode('utf-8'), bcrypt.gensalt())
        account.password = hashed_password.decode('utf-8')

        self.dao.add_account(account)
        return True, "Đăng ký thành công!"

    def login(self, user_id, input_password):
        user = self.dao.get_account_by_id(user_id)
        if user is None:
            return False, "Sai mã người dùng!"

        if bcrypt.checkpw(input_password.encode('utf-8'), user.password.encode('utf-8')):
            return True, "Đăng nhập thành công!"
        else:
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