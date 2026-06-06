import cv2
import os
from pyzbar.pyzbar import decode, ZBarSymbol

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