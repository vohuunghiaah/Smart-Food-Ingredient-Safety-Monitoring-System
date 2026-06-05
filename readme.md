# 🍽️ Smart Food Ingredient Safety Monitoring System

Hệ thống giám sát an toàn thành phần thực phẩm thông minh — hỗ trợ quét mã vạch sản phẩm, tra cứu thành phần, và cảnh báo dị ứng cho người dùng.

---

## 📋 Yêu cầu hệ thống

| Thành phần | Yêu cầu |
|---|---|
| **Hệ điều hành** | Windows 10/11 (64-bit) |
| **Python** | 3.10 – 3.12 (khuyến nghị 3.11.x) |
| **Database** | Microsoft SQL Server 2019+ (hoặc SQL Server Express) |
| **ODBC Driver** | ODBC Driver 17 for SQL Server |
| **Visual C++** | Visual C++ 2013 Redistributable (x64) ⚠️ **Bắt buộc** |
| **Camera** | Webcam (cho chức năng quét mã vạch) |

---

## 🚀 Hướng dẫn Cài đặt Môi trường

### Bước 1: Clone Project

```bash
git clone https://github.com/<your-username>/Smart-Food-Ingredient-Safety-Monitoring-System.git
cd Smart-Food-Ingredient-Safety-Monitoring-System
```

### Bước 2: Cài đặt Visual C++ 2013 Redistributable (x64)

> ⚠️ **BẮT BUỘC** — Thư viện `pyzbar` (quét mã vạch) phụ thuộc vào `MSVCR120.dll` từ Visual C++ 2013 Runtime. Nếu không cài, ứng dụng sẽ báo lỗi `FileNotFoundError: Could not find module libzbar-64.dll`.

📥 Tải tại: [Visual C++ Redistributable for VS 2013 (x64)](https://aka.ms/highdpimfc2013x64enu)

Hoặc truy cập: https://www.microsoft.com/en-us/download/details.aspx?id=40784

- Chạy file `vcredist_x64.exe` và làm theo hướng dẫn cài đặt.

### Bước 3: Cài đặt ODBC Driver 17 for SQL Server

📥 Tải tại: [Microsoft ODBC Driver 17 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

### Bước 4: Tạo Virtual Environment

```bash
python -m venv venv
```

### Bước 5: Kích hoạt Virtual Environment

```bash
# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Windows (CMD)
venv\Scripts\activate.bat
```

> 💡 Nếu gặp lỗi `Execution Policy` trên PowerShell, chạy trước:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### Bước 6: Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

### Bước 7: Kiểm tra cài đặt

```bash
# Kiểm tra pyzbar load thành công
python -c "from pyzbar.pyzbar import decode; print('pyzbar OK')"

# Kiểm tra kết nối database
python test_connection.py
```

---

## 🗄️ Cài đặt Database

### Bước 1: Cấu hình SQL Server

Mở file `utils/database_config.py` và đổi tên server thành tên máy tính của bạn:

```python
import pyodbc

def database_config():
    return pyodbc.connect(
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=\\<TÊN_MÁY_TÍNH_CỦA_BẠN>;"  # ← Thay đổi tại đây
        "Database=FOOD;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
```

> 💡 Để xem tên máy tính, mở CMD và gõ `hostname`.

### Bước 2: Chạy SQL Script

Mở **SQL Server Management Studio (SSMS)** và thực thi lần lượt:

1. `data/SQL.sql` — Tạo database và bảng
2. `data/update_sql.sql` — Nhập dữ liệu mẫu

---

## ▶️ Chạy ứng dụng

```bash
# Đảm bảo đã kích hoạt venv
venv\Scripts\activate

# Chạy ứng dụng
python -m src.main
```

---

## 📁 Cấu trúc Dự án

```
Smart-Food-Ingredient-Safety-Monitoring-System/
├── data/                          # SQL scripts
│   ├── SQL.sql                    # Script tạo database
│   └── update_sql.sql             # Script nhập dữ liệu
├── src/                           # Source code chính
│   ├── main.py                    # Entry point
│   ├── account/                   # Module quản lý tài khoản
│   │   ├── AccountBUS.py          # Business logic
│   │   ├── AccountDAO.py          # Data access
│   │   └── AccountDTO.py          # Data transfer object
│   ├── allergen_checker/          # Module kiểm tra dị ứng
│   │   ├── AllergenCheckerBUS.py  # Business logic
│   │   ├── AllergenCheckerDAO.py  # Data access
│   │   └── AllergenCheckerDTO.py  # Data transfer object
│   ├── ingredient/                # Module thành phần
│   └── scanner/                   # Module quét mã vạch
│       └── scanner.py             # Camera & barcode scanning
├── utils/                         # Tiện ích
│   └── database_config.py         # Cấu hình kết nối DB
├── requirements.txt               # Python dependencies
└── readme.md                      # File này
```

---

## ❓ Xử lý Lỗi Thường Gặp

### Lỗi: `FileNotFoundError: Could not find module libzbar-64.dll`

**Nguyên nhân**: Thiếu Visual C++ 2013 Redistributable (x64).  
**Giải pháp**: Cài đặt từ [link tải](https://aka.ms/highdpimfc2013x64enu).

### Lỗi: `InterfaceError: ('IM002', ... ODBC Driver 17 ...)`

**Nguyên nhân**: Chưa cài ODBC Driver 17 for SQL Server.  
**Giải pháp**: Tải và cài từ [trang Microsoft](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server).

### Lỗi: `pyodbc.OperationalError: Login failed`

**Nguyên nhân**: Sai tên server trong `database_config.py`.  
**Giải pháp**: Đổi tên server thành tên máy tính của bạn (gõ `hostname` trong CMD).

### Lỗi: `Execution Policy` khi kích hoạt venv trên PowerShell

**Giải pháp**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```