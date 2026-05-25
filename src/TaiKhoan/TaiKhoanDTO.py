class TaiKhoanDTO:
    def __init__(self, ma_nd, ten_nd, sdt, mat_khau):
        self.ma_nguoi_dung = ma_nd
        self.ten_nguoi_dung = ten_nd
        self.so_dien_thoai = sdt
        self.mat_khau = mat_khau
#mang rong
        self.danh_sach_di_ung = []