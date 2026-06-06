import json
import os
import cv2
from flask import Flask, render_template, Response, jsonify
from pyzbar.pyzbar import decode, ZBarSymbol
from scanner.export import get_product_details, get_product_from_openfoodfacts

app = Flask(__name__)

current_product = {
    "barcode": None,
    "name": None,
    "category": None,
    "ingredients": []
}


def process_barcode(barcode_val):
    global current_product
    if barcode_val == current_product["barcode"]:
        return

    current_product["barcode"] = barcode_val
    db_rows = get_product_details(barcode_val)

    if db_rows:
        current_product["name"] = db_rows[0][1]
        current_product["category"] = db_rows[0][2]
        current_product["ingredients"] = [item[3] for item in db_rows]
    else:
        food = get_product_from_openfoodfacts(barcode_val)
        if food:
            current_product["name"] = food["name"]
            current_product["category"] = food["category"]
            current_product["ingredients"] = food["ingredients"]
        else:
            current_product["name"] = "Không tìm thấy"
            current_product["category"] = "Không tìm thấy"
            current_product["ingredients"] = []


def generate_video_stream():
    os.environ['ZBAR_NONE'] = '1'
    camera = cv2.VideoCapture(0)
    camera.set(3, 640)
    camera.set(4, 360)

    while True:
        success, frame = camera.read()
        if not success:
            break

        barcodes = decode(frame, symbols=[ZBarSymbol.EAN13, ZBarSymbol.CODE128])
        for barcode in barcodes:
            barcode_val = barcode.data.decode("utf-8")
            process_barcode(barcode_val)

            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (46, 204, 113), 3)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    camera.release()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/get_data')
def get_data():
    return jsonify(current_product)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)