import re
import pyodbc
import requests
from deep_translator import GoogleTranslator

SERVER = 'DESKTOP-1PJL28F'
DATABASE_NAME = 'AllergyDB'
USERNAME = 'sa'
PASSWORD = 'Tien@2208'


def get_connection_string():
    return (
        f"Driver={{ODBC Driver 17 for SQL Server}};"
        f"Server={SERVER};"
        f"Database={DATABASE_NAME};"
        f"UID={USERNAME};"
        f"PWD={PASSWORD};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )


def split_ingredients(text):
    if not text:
        return []

    text = re.sub(r'(\d)\s*,\s*(\d)', r'\1[DOT]\2', text)
    pattern = r',(?![^()]*\))'
    raw_ingredients = re.split(pattern, text)

    cleaned_ingredients = []
    for x in raw_ingredients:
        item = x.strip()
        if item:
            item = item.replace('[DOT]', ',')
            cleaned_ingredients.append(item)

    return cleaned_ingredients


def get_product_details(barcode_val):
    try:
        conn = pyodbc.connect(get_connection_string())
        cursor = conn.cursor()
        query = """
                SELECT s.ma_san_pham, s.ten_san_pham, n.ten_nhom, t.ten_thanh_phan
                FROM SanPham s
                         JOIN NhomSanPham n ON s.ma_nhom_san_pham = n.ma_nhom
                         JOIN ThanhPhanSanPham ts ON s.ma_san_pham = ts.ma_san_pham
                         JOIN ThanhPhan t ON ts.ma_thanh_phan = t.ma_thanh_phan
                WHERE s.ma_vach = ?
                """
        cursor.execute(query, (barcode_val,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"[!] Query Error: {e}")
        return []


def get_product_from_openfoodfacts(barcode):
    try:
        url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}"
        headers = {"User-Agent": "AllergyChecker/1.0", "Accept": "application/json"}
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code != 200: return None
        data = response.json()
        if data.get("status") != 1: return None

        product = data.get("product", {})

        product_name = product.get("product_name_vi") or product.get("product_name") or "Không xác định"
        try:
            product_name = GoogleTranslator(source="auto", target="vi").translate(product_name)
        except:
            pass

        category = product.get("categories_vi") or product.get("categories") or "Không xác định"
        category = category.replace("en:", "").replace("fr:", "").replace("vi:", "")
        try:
            category = GoogleTranslator(source="auto", target="vi").translate(category)
        except:
            pass

        ingredients = []
        translated_text = ""
        ingredients_text = product.get("ingredients_text_vi") or product.get("ingredients_text") or ""

        if ingredients_text:
            try:
                translated_text = GoogleTranslator(source="auto", target="vi").translate(ingredients_text)
                ingredients = split_ingredients(translated_text)
            except:
                ingredients = split_ingredients(ingredients_text)
        else:
            for ing in product.get("ingredients", []):
                name = ing.get("text")
                if name: ingredients.append(name)

        return {
            "name": product_name,
            "category": category,
            "ingredients": ingredients,
            "ingredients_text": translated_text
        }
    except Exception as e:
        print(f"[!] OpenFoodFacts Error: {e}")
        return None


def main():
    import os
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    try:
        from scanner.scanner import scan_barcode_from_camera
    except ImportError:
        from scanner import scan_barcode_from_camera

    barcode = scan_barcode_from_camera()
    if barcode:
        print(f"\n[+] ĐANG TIẾN HÀNH KIỂM TRA MÃ VẠCH: {barcode}")

        # 1. Thử tìm trong Database nội bộ
        details = get_product_details(barcode)
        if details:
            print("\n" + "=" * 23 + " KẾT QUẢ TỪ DATABASE " + "=" * 23)
            print(f"  Sản phẩm  : {details[0][1]}")
            print(f"  Phân nhóm : {details[0][2]}")
            print("-" * 65)
            print("  Thành phần phân tích từ Hệ thống:")
            for item in details:
                print(f"    - {item[3]}")
            print("=" * 65)

        # 2. Nếu Database không có, thông báo chuyển sang OpenFoodFacts
        else:
            print("\n[!] Không tìm thấy sản phẩm này trong Database nội bộ.")
            print("[*] Đang tiến hành kết nối API OpenFoodFacts trực tuyến...")

            food = get_product_from_openfoodfacts(barcode)
            if food:
                print("\n" + "=" * 24 + " KẾT QUẢ " + "=" * 24)
                print(f"  Sản phẩm  : {food['name']}")
                print(f"  Phân nhóm : {food['category']}")
                print("-" * 65)
                print("  Thành phần phân tích từ Cloud:")
                for ing in food['ingredients']:
                    print(f"    - {ing}")
                print("=" * 65)
            else:
                print("[X] Mã vạch này không tồn tại trên hệ thống dữ liệu OpenFoodFacts.")


if __name__ == "__main__":
    main()