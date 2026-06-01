import cv2
from pyzbar.pyzbar import decode, ZBarSymbol
import pyodbc
import os
import requests

# Kết nối SQL Server
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
                SELECT s.ma_san_pham,
                       s.ten_san_pham,
                       n.ten_nhom,
                       t.ten_thanh_phan
                FROM SanPham s
                         JOIN NhomSanPham n
                              ON s.ma_nhom_san_pham = n.ma_nhom
                         JOIN ThanhPhanSanPham ts
                              ON s.ma_san_pham = ts.ma_san_pham
                         JOIN ThanhPhan t
                              ON ts.ma_thanh_phan = t.ma_thanh_phan
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

        headers = {
            "User-Agent": "AllergyChecker/1.0",
            "Accept": "application/json"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            return None

        data = response.json()

        product = data.get("product", {})

        categories = product.get("categories_tags", [])

        category = ", ".join(
            tag.replace("en:", "").replace("-", " ").title()
            for tag in categories[:5]
        )

        if not category:
            category = "Unknown Category"

        ingredients = []

        ingredients_text = product.get("ingredients_text_en", "")

        if ingredients_text:
            ingredients = [
                x.strip().capitalize()
                for x in ingredients_text.split(",")
                if x.strip()
            ]
        else:
            for ing in product.get("ingredients", []):
                name = ing.get("text")
                if name:
                    ingredients.append(name)

        return {
            "name": product.get("product_name", "Unknown Product"),
            "category": category,
            "ingredients": ingredients
        }

    except Exception as e:
        print(f"[!] OpenFoodFacts Error: {e}")
        return None

def main():

    os.environ['ZBAR_NONE'] = '1'

    cap = cv2.VideoCapture(0)

    cap.set(3, 1280)
    cap.set(4, 720)

    print("\n" + "=" * 50)
    print("ALLERGY CHECKER SYSTEM")
    print("Connecting to existing Database: " + DATABASE_NAME)
    print("Point camera at barcode...")
    print("=" * 50 + "\n")

    scanned_barcode = None

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        barcodes = decode(
            frame,
            symbols=[
                ZBarSymbol.EAN13,
                ZBarSymbol.CODE128
            ]
        )

        for barcode in barcodes:

            scanned_barcode = barcode.data.decode("utf-8")

            (x, y, w, h) = barcode.rect

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                3
            )

            cv2.imshow('Scanner', frame)

            cv2.waitKey(800)

            break

        if scanned_barcode:
            break

        cv2.imshow('Scanner', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if scanned_barcode:

        print(f"\n[+] SCANNED BARCODE: {scanned_barcode}")

        details = get_product_details(scanned_barcode)

        # Có trong SQL Server
        if details:

            print(f"\nID: {details[0][0]}")
            print(f"NAME: {details[0][1]}")
            print(f"CATEGORY: {details[0][2]}")

            print("INGREDIENTS:")

            for item in details:
                print(f"  - {item[3]}")

        # Không có trong SQL -> Open Food Facts
        else:

            print("\n[!] Product not found in local database.")
            print("[*] Searching Open Food Facts...")

            food = get_product_from_openfoodfacts(
                scanned_barcode
            )

            if food:

                print("\n===== OPEN FOOD FACTS RESULT =====")

                print(f"NAME: {food['name']}")
                print(f"CATEGORY: {food['category']}")

                print("INGREDIENTS:")

                if food["ingredients"]:
                    for ing in food["ingredients"]:
                        print(f"  - {ing}")
                else:
                    print("  No ingredient data available")

            else:
                print("[X] Product not found on Open Food Facts.")

        print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
