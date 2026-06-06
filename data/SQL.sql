-- =========================================================================
-- SMART FOOD INGREDIENT SAFETY MONITORING SYSTEM
-- Script gom toàn bộ: Tạo Database, Bảng, và Dữ liệu mẫu
-- Chạy file này 1 lần duy nhất trong SSMS để khởi tạo hệ thống
-- =========================================================================

-- 1. ĐỊNH VỊ ĐÚNG DATABASE
USE [FOOD];
GO

-- 2. XÓA BẢNG CŨ NẾU CÓ (Tránh lỗi đã tồn tại khi chạy lại)
-- Phải xóa bảng con trước, bảng cha sau
DROP TABLE IF EXISTS LichSuQuet;
DROP TABLE IF EXISTS ThanhPhanSanPham;
DROP TABLE IF EXISTS ThanhPhanDiUng;
DROP TABLE IF EXISTS TenGoiKhac;
DROP TABLE IF EXISTS TaiKhoan;
DROP TABLE IF EXISTS SanPham;
DROP TABLE IF EXISTS ThanhPhan;
DROP TABLE IF EXISTS NhomSanPham;
GO

-- ==========================================
-- 3. KHỞI TẠO CẤU TRÚC BẢNG (SCHEMA)
-- ==========================================
CREATE TABLE NhomSanPham (
    ma_nhom varchar(10) PRIMARY KEY,
    ten_nhom nvarchar(50)
);

CREATE TABLE SanPham (
    ma_san_pham varchar(10) PRIMARY KEY, 
    ma_vach VARCHAR(50) NOT NULL UNIQUE,
    ten_san_pham NVARCHAR(150) NOT NULL, 
    ma_nhom_san_pham varchar(10),
    FOREIGN KEY (ma_nhom_san_pham) REFERENCES NhomSanPham(ma_nhom) ON DELETE CASCADE
);

CREATE TABLE ThanhPhan (
    ma_thanh_phan varchar(10) PRIMARY KEY, 
    ten_thanh_phan NVARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE TaiKhoan (
    ma_nguoi_dung varchar(10) PRIMARY KEY,
    ten_nguoi_dung nvarchar(50),
    so_dien_thoai varchar(10),
    mat_khau varchar(255) -- Tăng lên 255 để chứa bcrypt hash (60 ký tự)
);

CREATE TABLE TenGoiKhac (
     ma_thanh_phan varchar(10),
     ma_ten_goi_khac varchar(10) PRIMARY KEY,
     ten_goi_khac nvarchar(50),
     FOREIGN KEY (ma_thanh_phan) REFERENCES ThanhPhan(ma_thanh_phan) ON DELETE CASCADE
);

CREATE TABLE ThanhPhanDiUng (
     ma_nguoi_dung varchar(10),
     ma_thanh_phan varchar(10),
    PRIMARY KEY (ma_nguoi_dung, ma_thanh_phan),
    FOREIGN KEY (ma_nguoi_dung) REFERENCES TaiKhoan(ma_nguoi_dung) ON DELETE CASCADE,
    FOREIGN KEY (ma_thanh_phan) REFERENCES ThanhPhan(ma_thanh_phan) ON DELETE CASCADE
);

CREATE TABLE ThanhPhanSanPham (
    ma_san_pham varchar(10),
    ma_thanh_phan varchar(10),
    PRIMARY KEY (ma_san_pham, ma_thanh_phan),
    FOREIGN KEY (ma_san_pham) REFERENCES SanPham(ma_san_pham) ON DELETE CASCADE,
    FOREIGN KEY (ma_thanh_phan) REFERENCES ThanhPhan(ma_thanh_phan) ON DELETE CASCADE
);

CREATE TABLE LichSuQuet (
    id INT IDENTITY(1,1) PRIMARY KEY,
    ma_nguoi_dung VARCHAR(10),
    ma_vach VARCHAR(50),
    ten_san_pham NVARCHAR(150),
    muc_canh_bao VARCHAR(20),
    thoi_gian DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (ma_nguoi_dung) REFERENCES TaiKhoan(ma_nguoi_dung) ON DELETE CASCADE
);
GO

-- ==========================================
-- 4. CHÈN DỮ LIỆU MẪU
-- ==========================================
INSERT INTO NhomSanPham (ma_nhom, ten_nhom) VALUES 
('N01', N'Sữa và sản phẩm từ sữa'),
('N02', N'Bánh kẹo'),
('N03', N'Đồ uống giải khát'),
('N04', N'Mì liền và Đồ đóng hộp');

INSERT INTO SanPham (ma_san_pham, ma_vach, ten_san_pham, ma_nhom_san_pham) VALUES
('SP01', '8934673576390', N'100 % fresh milk Vinamilk', 'N01'),
('SP02', '7622300442507', N'Bánh Oreo', 'N02'),
('SP03', '8934588232114', N'Nước tăng lực Sting hương dâu', 'N03'),
('SP04', '8934563138165', N'Mì ăn liền Hảo Hảo tôm chua cay', 'N04');

INSERT INTO ThanhPhan (ma_thanh_phan, ten_thanh_phan) VALUES
('TP01', N'Sữa bò'), ('TP02', N'Đậu phộng'), ('TP03', N'lúa mì'),
('TP04', N'Phẩm màu nhân tạo'), ('TP05', N'Dâu'), ('TP06', N'Ca cao'),
('TP07', N'Muối'), ('TP08', N'Đường'), ('TP09', N'Nước mắm'),
('TP10', N'Bột nghệ'), ('TP11', N'Dầu cọ'), ('TP12', N'Tôm'),
('TP13', N'Cá'), ('TP14', N'Tỏi'), ('TP15', N'Bột ớt'),
('TP16', N'Hành lá'), ('TP17', N'Ngò '), ('TP18', N'Gừng'),
('TP19', N'Bắp'), ('TP20', N'Hương vani'), ('TP21', N'Đậu nành'),
('TP22', N'Hương dâu '), ('TP23', N'Nước bão hòa CO2'), ('TP24', N'Hồng sâm'),
('TP25', N'Caffeine'), ('TP26', N'Chất điều chỉnh độ axit (330, 331())'),
('TP27', N'Chất chống oxy hóa (452(j)'), ('TP28', N'Chất bảo quản (202, 211)'),
('TP29', N'Taurine'), ('TP30', N'Nicotinamide'), ('TP31', N'Inositol');

INSERT INTO TaiKhoan (ma_nguoi_dung, ten_nguoi_dung, so_dien_thoai, mat_khau) VALUES
('U00', N'admin', '0123456789', 'admin123'),
('U01', N'Nguyễn Văn Nam', '0912345678', 'hash_nam_123'),
('U02', N'Lê Minh Tiến', '0923456789', 'hash_tien_456'),
('U03', N'Trần Bảo Ngọc', '0934567890', 'hash_ngoc_789'),
('U04', N'Phạm Thị Thu', '0945678901', 'hash_thu_000');

INSERT INTO TenGoiKhac (ma_thanh_phan, ma_ten_goi_khac, ten_goi_khac) VALUES
('TP01', 'TGK01', N'Lactose'), ('TP01', 'TGK02', N'Whey Protein'), 
('TP03', 'TGK03', N'Bột mì'), ('TP04', 'TGK04', N'Màu tổng hợp Allura Red'),
('TP06', 'TGK05', N'Socola'), ('TP03', 'TGK06', N'Tinh bột khoai mì'),
('TP03', 'TGK07', N'Khoai mì');

INSERT INTO ThanhPhanDiUng (ma_nguoi_dung, ma_thanh_phan) VALUES
('U01', 'TP01'), ('U01', 'TP02'), ('U02', 'TP03'), ('U03', 'TP04'); 

INSERT INTO ThanhPhanSanPham (ma_san_pham, ma_thanh_phan) VALUES
('SP01', 'TP01'), 
('SP02', 'TP01'), ('SP02', 'TP03'), ('SP02', 'TP06'), ('SP02', 'TP19'), ('SP02', 'TP20'), ('SP02', 'TP21'),
('SP03', 'TP05'), ('SP03', 'TP22'), ('SP03', 'TP23'), ('SP03', 'TP24'), ('SP03', 'TP25'), ('SP03', 'TP26'), ('SP03', 'TP27'), ('SP03', 'TP28'), ('SP03', 'TP29'), ('SP03', 'TP30'), ('SP03', 'TP31'),
('SP04', 'TP03'), ('SP04', 'TP07'), ('SP04', 'TP08'), ('SP04', 'TP09'), ('SP04', 'TP10'), ('SP04', 'TP11'), ('SP04', 'TP12'), ('SP04', 'TP13'), ('SP04', 'TP14'), ('SP04', 'TP15'), ('SP04', 'TP16'), ('SP04', 'TP17');
GO