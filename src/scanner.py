import cv2
from pyzbar.pyzbar import decode, ZBarSymbol
import pyodbc
import os

# Kết nối
SERVER = 'server' #bỏ tên server vào, vd: DESKTOP-1PJL28F
DATABASE_NAME = 'AllergyDB'
USERNAME = 'sa'
PASSWORD = 'password' #bỏ pass sql server của mn vào


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

        # Query to fetch ID, Name, Category, and Ingredient
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


def main():

    os.environ['ZBAR_NONE'] = '1'
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    print("\n" + "=" * 50)
    print("ALLERGY CHECKER SYSTEM (READ-ONLY MODE)")
    print("Connecting to existing Database: " + DATABASE_NAME)
    print("Point camera at barcode...")
    print("=" * 50 + "\n")

    scanned_barcode = None
    while True:
        ret, frame = cap.read()
        if not ret: break

        #Hiện chỉ quét được mã ean-13 và code128
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

    if scanned_barcode:
        print(f"\n[+] SCANNED BARCODE: {scanned_barcode}")
        details = get_product_details(scanned_barcode)

        if details:
            print(f"ID: {details[0][0]}")
            print(f"NAME: {details[0][1]}")
            print(f"CATEGORY: {details[0][2]}")
            print("INGREDIENTS:")
            for item in details:
                print(f"  - {item[3]}")
        else:
            print("[?] No record found in system. Please check your SQL Server data.")
        print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
