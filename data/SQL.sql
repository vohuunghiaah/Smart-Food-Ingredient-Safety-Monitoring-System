-- =========================================================================
-- ĐẢM BẢO CHẠY CÁC LỆNH TẠO BẢNG THEO THỨ TỰ NÀY TRƯỚC
-- =========================================================================

-- 1. Tạo bảng nhóm sản phẩm (Phải tạo đầu tiên)
CREATE TABLE NhomSanPham (
	ma_nhom varchar(10) PRIMARY KEY,
	ten_nhom nvarchar(50)
);

-- 2. Tạo bảng Sản phẩm
CREATE TABLE SanPham (
    ma_san_pham varchar(10) PRIMARY KEY, 
    ma_vach VARCHAR(50) NOT NULL UNIQUE,
    ten_san_pham NVARCHAR(150) NOT NULL, 
    ma_nhom_san_pham varchar(10), -- Sửa lại kiểu dữ liệu thành varchar(10) cho đồng bộ với ma_nhom
	FOREIGN KEY (ma_nhom_san_pham) REFERENCES NhomSanPham(ma_nhom) ON DELETE CASCADE
);

-- 3. Tạo bảng Thành phần
CREATE TABLE ThanhPhan (
    ma_thanh_phan varchar(10) PRIMARY KEY, 
    ten_thanh_phan NVARCHAR(100) NOT NULL UNIQUE
);

-- 4. Tạo bảng tài khoản
CREATE TABLE TaiKhoan (
	ma_nguoi_dung varchar(10) PRIMARY KEY,
	ten_nguoi_dung nvarchar(50),
	so_dien_thoai varchar(10),
	mat_khau varchar(50)
);

-- 5. Tạo bảng tên gọi khác
CREATE TABLE TenGoiKhac (
	 ma_thanh_phan varchar(10),
	 ma_ten_goi_khac varchar(10) PRIMARY KEY,
	 ten_goi_khac nvarchar(50),
	 FOREIGN KEY (ma_thanh_phan) REFERENCES ThanhPhan(ma_thanh_phan) ON DELETE CASCADE
);

-- 6. Tạo bảng thành phần dị ứng của user
CREATE TABLE ThanhPhanDiUng (
	 ma_nguoi_dung varchar(10),
	 ma_thanh_phan varchar(10),
	PRIMARY KEY (ma_nguoi_dung, ma_thanh_phan),
    FOREIGN KEY (ma_nguoi_dung) REFERENCES TaiKhoan(ma_nguoi_dung) ON DELETE CASCADE,
    FOREIGN KEY (ma_thanh_phan) REFERENCES ThanhPhan(ma_thanh_phan) ON DELETE CASCADE
);

-- 7. Tạo bảng thành phần sản phẩm
CREATE TABLE ThanhPhanSanPham (
    ma_san_pham varchar(10),
    ma_thanh_phan varchar(10),
    PRIMARY KEY (ma_san_pham, ma_thanh_phan),
    FOREIGN KEY (ma_san_pham) REFERENCES SanPham(ma_san_pham) ON DELETE CASCADE,
    FOREIGN KEY (ma_thanh_phan) REFERENCES ThanhPhan(ma_thanh_phan) ON DELETE CASCADE
);




-- 1. Chèn bảng NhomSanPham
INSERT INTO NhomSanPham (ma_nhom, ten_nhom) VALUES 
('N01', N'Sữa và sản phẩm từ sữa'),
('N02', N'Bánh kẹo'),
('N03', N'Đồ uống giải khát'),
('N04', N'Mì liền và Đồ đóng hộp');

-- 2. Chèn bảng SanPham 
INSERT INTO SanPham (ma_san_pham, ma_vach, ten_san_pham, ma_nhom_san_pham) VALUES
('SP01', '8934563123456', N'Sữa tươi tiệt trùng Vinamilk', 'N01'),
('SP02', '8934563777777', N'Bánh sô-cô-la Oreo', 'N02'),
('SP03', '8934563888888', N'Nước tăng lực Sting dâu', 'N03'),
('SP04', '8934563999999', N'Mì ăn liền Hảo Hảo tôm chua cay', 'N04');

-- 3. Chèn bảng ThanhPhan 
INSERT INTO ThanhPhan (ma_thanh_phan, ten_thanh_phan) VALUES
('TP01', N'Sữa bò'),
('TP02', N'Đậu phộng'),
('TP03', N'lúa mì'),
('TP04', N'Phẩm màu nhân tạo'),
('TP05', N'Dâu'),
('TP06', N'Ca cao');

-- 4. Chèn bảng TaiKhoan 
INSERT INTO TaiKhoan (ma_nguoi_dung, ten_nguoi_dung, so_dien_thoai, mat_khau) VALUES
('U01', N'Nguyễn Văn Nam', '0912345678', 'hash_nam_123'),
('U02', N'Lê Minh Tiến', '0923456789', 'hash_tien_456'),
('U03', N'Trần Bảo Ngọc', '0934567890', 'hash_ngoc_789'),
('U04', N'Phạm Thị Thu', '0945678901', 'hash_thu_000');

-- 5. Chèn bảng TenGoiKhac 
INSERT INTO TenGoiKhac (ma_thanh_phan, ma_ten_goi_khac, ten_goi_khac) VALUES
('TP01', 'TGK01', N'Lactose'),      
('TP01', 'TGK02', N'Whey Protein'), 
('TP03', 'TGK03', N'Bột mì'),
('TP04', 'TGK04', N'Màu tổng hợp Allura Red'),
('TP06', 'TGK05', N'Socola');
-- 6. Chèn bảng ThanhPhanDiUng 
INSERT INTO ThanhPhanDiUng (ma_nguoi_dung, ma_thanh_phan) VALUES
('U01', 'TP01'), 
('U01', 'TP02'), 
('U02', 'TP03'), 
('U03', 'TP04'); 

-- 7. Chèn bảng ThanhPhanSanPham 
INSERT INTO ThanhPhanSanPham (ma_san_pham, ma_thanh_phan) VALUES
('SP01', 'TP01'), 
('SP02', 'TP01'), 
('SP02', 'TP06'),
('SP02', 'TP03'), 
('SP04', 'TP03'),
('SP03', 'TP05');