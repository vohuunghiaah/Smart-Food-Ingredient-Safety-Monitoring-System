import bcrypt
from TaiKhoanDAO import TaiKhoanDAO

class TaiKhoanBUS:
    def __init__(self):
        self.dao = TaiKhoanDAO()

    def dang_ky(self, tk):
        if tk.ma_nguoi_dung == "" or tk.mat_khau == "":
            return False, "Không được để trống thông tin!"

        ktra_tk = self.dao.lay_tai_khoan_theo_ma(tk.ma_nguoi_dung)
        if ktra_tk != None:
            return False, "Tài khoản đã tồn tại!"


        mk_bam = bcrypt.hashpw(tk.mat_khau.encode('utf-8'), bcrypt.gensalt())
        tk.mat_khau = mk_bam.decode('utf-8')

        self.dao.them_tai_khoan(tk)
        return True, "Đăng ký thành công!"

    def dang_nhap(self, ma_nguoi_dung, mat_khau_nhap):
        user = self.dao.lay_tai_khoan_theo_ma(ma_nguoi_dung)
        if user == None:
            return False, "Sai mã người dùng!"


        if bcrypt.checkpw(mat_khau_nhap.encode('utf-8'), user.mat_khau.encode('utf-8')):
            return True, "Đăng nhập thành công!"
        else:
            return False, "Sai mật khẩu!"

    def thiet_lap_profile(self, ma_nguoi_dung, ten_moi, sdt_moi, ds_di_ung):
        user = self.dao.lay_tai_khoan_theo_ma(ma_nguoi_dung)
        if user == None:
            return False, "Không tìm thấy user!"

        user.ten_nguoi_dung = ten_moi
        user.so_dien_thoai = sdt_moi
        user.danh_sach_di_ung = ds_di_ung

        self.dao.cap_nhat_profile_va_di_ung(user)
        return True, "Lưu profile thành công!"