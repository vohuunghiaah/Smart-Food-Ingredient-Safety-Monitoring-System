# 🛡️ Smart Food Ingredient Safety Monitoring System

Hệ thống giám sát an toàn thành phần thực phẩm thông minh — quét mã vạch sản phẩm, tra cứu thành phần, cảnh báo dị ứng cho người dùng.

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

## ✨ Tính năng chính

- 📷 **Quét mã vạch** sản phẩm bằng webcam (EAN13, CODE128)
- ⚠️ **Cảnh báo dị ứng** tự động theo 5 mức độ (An toàn → Nguy hiểm)
- 📱 **Đăng nhập / Đăng ký** bằng số điện thoại
- 👤 **Hồ sơ cá nhân** — quản lý danh sách chất dị ứng (thêm, xem, xóa)
- 📋 **Lịch sử quét** — xem lại các sản phẩm đã quét
- 🌐 **Tra cứu mở rộng** — tìm sản phẩm qua OpenFoodFacts API khi không có trong DB

---

## 🚀 Hướng dẫn Cài đặt

### Bước 1: Clone Project

```bash
git clone https://github.com/<your-username>/Smart-Food-Ingredient-Safety-Monitoring-System.git
cd Smart-Food-Ingredient-Safety-Monitoring-System
```

### Bước 2: Cài đặt Visual C++ 2013 Redistributable (x64)

> ⚠️ **BẮT BUỘC** — Thư viện `pyzbar` phụ thuộc vào `MSVCR120.dll` từ Visual C++ 2013 Runtime.

📥 Tải tại: [Visual C++ Redistributable for VS 2013 (x64)](https://aka.ms/highdpimfc2013x64enu)

### Bước 3: Cài đặt ODBC Driver 17 for SQL Server

📥 Tải tại: [Microsoft ODBC Driver 17](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

### Bước 4: Tạo và kích hoạt Virtual Environment

```bash
python -m venv venv

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Windows (CMD)
venv\Scripts\activate.bat
```

> 💡 Nếu gặp lỗi `Execution Policy` trên PowerShell, chạy trước:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### Bước 5: Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

### Bước 6: Kiểm tra cài đặt

```bash
# Kiểm tra pyzbar load thành công
python -c "from pyzbar.pyzbar import decode; print('pyzbar OK')"

# Kiểm tra kết nối database
python -c "from utils.database_config import database_config; conn = database_config(); print('DB OK'); conn.close()"
```

---

## 🗄️ Cài đặt Database

### Bước 1: Cấu hình kết nối

Mở file `utils/database_config.py` và đổi tên server thành tên máy tính của bạn:

```python
import pyodbc

def database_config():
    return pyodbc.connect(
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=<TÊN_MÁY_TÍNH_CỦA_BẠN>;"  # ← Thay đổi tại đây
        "Database=FOOD;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
```

> 💡 Để xem tên máy tính, mở CMD và gõ `hostname`.

### Bước 2: Tạo Database và dữ liệu mẫu

1. Mở **SQL Server Management Studio (SSMS)**
2. Tạo database `FOOD` nếu chưa có:
   ```sql
   CREATE DATABASE FOOD;
   ```
3. Chạy file **`data/SQL.sql`** — tạo toàn bộ bảng + nhập dữ liệu mẫu (chỉ cần chạy 1 file duy nhất)

---

## ▶️ Chạy ứng dụng

```bash
# Đảm bảo đã kích hoạt venv
venv\Scripts\activate

# Chạy web app
cd src
python web_app.py
```

Truy cập trình duyệt: **http://localhost:5000**

### Tài khoản mẫu

| SĐT | Mật khẩu | Tên |
|-----|----------|-----|
| 0912345678 | hash_nam_123 | Nguyễn Văn Nam |
| 0923456789 | hash_tien_456 | Lê Minh Tiến |
| 0934567890 | hash_ngoc_789 | Trần Bảo Ngọc |
| 0945678901 | hash_thu_000 | Phạm Thị Thu |

---

## 📁 Cấu trúc Dự án

```
Smart-Food-Ingredient-Safety-Monitoring-System/
├── data/                              # SQL scripts
│   └── SQL.sql                        # Script tạo DB + bảng + dữ liệu mẫu
├── src/                               # Source code chính
│   ├── web_app.py                     # ★ Entry point (Flask web app)
│   ├── main.py                        # CLI cũ (tham khảo)
│   ├── account/                       # Module quản lý tài khoản
│   │   ├── AccountBUS.py              # Business logic (login, register, profile)
│   │   ├── AccountDAO.py              # Data access (SQL queries)
│   │   └── AccountDTO.py              # Data transfer object
│   ├── allergen_checker/              # Module kiểm tra dị ứng
│   │   ├── AllergenCheckerBUS.py      # Logic so khớp dị ứng (alias, 5 mức)
│   │   ├── AllergenCheckerDAO.py      # Data access
│   │   └── AllergenCheckerDTO.py      # DTO (AllergenResult)
│   ├── ingredient/                    # Module thành phần
│   │   ├── IngredientDAO.py           # Truy vấn thành phần
│   │   └── IngredientDTO.py           # DTO
│   ├── history/                       # Module lịch sử quét
│   │   └── HistoryDAO.py              # Lưu/đọc lịch sử quét
│   ├── scanner/                       # Module quét mã vạch
│   │   ├── scanner.py                 # Camera & barcode scanning
│   │   └── export.py                  # Tra cứu sản phẩm (DB + OpenFoodFacts)
│   ├── static/                        # Static files
│   │   └── css/style.css              # Design system (dark theme)
│   └── templates/                     # Jinja2 HTML templates
│       ├── base.html                  # Layout gốc (navbar, flash messages)
│       ├── login.html                 # Đăng nhập
│       ├── register.html              # Đăng ký
│       ├── scanner.html               # Quét mã vạch + cảnh báo dị ứng
│       ├── profile.html               # Hồ sơ cá nhân + quản lý dị ứng
│       └── history.html               # Lịch sử quét
├── utils/                             # Tiện ích
│   └── database_config.py             # Cấu hình kết nối SQL Server
├── requirements.txt                   # Python dependencies
└── readme.md                          # File này
```

---

## 🏗️ Kiến trúc hệ thống

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Templates   │ ←── │   web_app.py │ ──→ │   BUS Layer  │
│  (HTML/CSS)  │     │  (Flask App) │     │ (Logic)      │
└─────────────┘     └──────────────┘     └──────┬───────┘
                                                 │
                                         ┌───────▼───────┐
                                         │   DAO Layer    │
                                         │ (SQL Queries)  │
                                         └───────┬───────┘
                                                 │
                                         ┌───────▼───────┐
                                         │  SQL Server    │
                                         │  (Database)    │
                                         └───────────────┘
```

**Mô hình 3 lớp:**
- **DTO** — Data Transfer Object: định nghĩa cấu trúc dữ liệu
- **DAO** — Data Access Object: thao tác trực tiếp với database (pyodbc)
- **BUS** — Business Logic: xử lý nghiệp vụ (hash mật khẩu, kiểm tra dị ứng, ...)

---

## ❓ Xử lý Lỗi Thường Gặp

### `FileNotFoundError: Could not find module libzbar-64.dll`
**Nguyên nhân**: Thiếu Visual C++ 2013 Redistributable (x64).  
**Giải pháp**: Cài đặt từ [link tải](https://aka.ms/highdpimfc2013x64enu).

### `InterfaceError: ('IM002', ... ODBC Driver 17 ...)`
**Nguyên nhân**: Chưa cài ODBC Driver 17 for SQL Server.  
**Giải pháp**: Tải và cài từ [trang Microsoft](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server).

### `pyodbc.OperationalError: Login failed / Named Pipes`
**Nguyên nhân**: SQL Server chưa bật hoặc sai tên server trong `database_config.py`.  
**Giải pháp**: 
1. Đảm bảo SQL Server đang chạy (kiểm tra trong Services).
2. Đổi tên server thành tên máy tính của bạn (gõ `hostname` trong CMD).

### `Execution Policy` khi kích hoạt venv trên PowerShell
**Giải pháp**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Không thể kết nối database khi login
**Nguyên nhân**: Ứng dụng hiển thị flash "Không thể kết nối đến cơ sở dữ liệu".  
**Giải pháp**: Kiểm tra SQL Server đang chạy và cấu hình đúng trong `utils/database_config.py`.