import cv2
from pyzbar.pyzbar import decode, ZBarSymbol
import pyodbc
import os
import requests
from deep_translator import GoogleTranslator


SERVER = 'server'
DATABASE_NAME = 'AllergyDB'
USERNAME = 'sa'
PASSWORD = 'pass'


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

        # Lấy và dịch tên sản phẩm
        product_name = product.get("product_name_vi") or product.get("product_name") or "Không xác định"
        try:
            product_name = GoogleTranslator(source="auto", target="vi").translate(product_name)
        except:
            pass

        # Lấy và dịch nhóm
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
                ingredients = [x.strip() for x in translated_text.split(",") if x.strip()]
            except:
                ingredients = [x.strip() for x in ingredients_text.split(",") if x.strip()]
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


def scan_barcode_from_camera():
    os.environ['ZBAR_NONE'] = '1'
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    print("\n[HỆ THỐNG] Đang mở Camera... Nhấn 'q' để thoát.")
    scanned_barcode = None

    while True:
        ret, frame = cap.read()
        if not ret: break

        barcodes = decode(frame, symbols=[ZBarSymbol.EAN13, ZBarSymbol.CODE128])
        for barcode in barcodes:
            scanned_barcode = barcode.data.decode("utf-8")
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            cv2.imshow('Scanner', frame)
            cv2.waitKey(800)
            break

        if scanned_barcode: break
        cv2.imshow('Scanner', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()
    return scanned_barcode


def main():
    #hàm main để test riêng file này
    barcode = scan_barcode_from_camera()
    if barcode:
        print(f"\n[+] MÃ VẠCH QUÉT ĐƯỢC: {barcode}")
        details = get_product_details(barcode)
        if details:
            print(f"NAME: {details[0][1]}")
            print("INGREDIENTS:", [item[3] for item in details])
        else:
            food = get_product_from_openfoodfacts(barcode)
            if food:
                print(f"NAME (OFF): {food['name']}")
                print(f"INGREDIENTS: {food['ingredients_text']}")


if __name__ == "__main__":
    main()