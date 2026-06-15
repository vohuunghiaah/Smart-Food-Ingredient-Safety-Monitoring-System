import json
import os
import sys
import cv2
import threading
from flask import Flask, render_template, Response, jsonify, request, redirect, url_for, session, flash
from pyzbar.pyzbar import decode, ZBarSymbol

# Đảm bảo import path đúng
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scanner.export import get_product_details, get_product_from_openfoodfacts
from account.AccountBUS import AccountBUS
from allergen_checker.AllergenCheckerBUS import AllergenCheckerBUS
from ingredient.IngredientDAO import IngredientDAO
from history.HistoryDAO import HistoryDAO

# ============================================================
# Flask App Configuration
# ============================================================
app = Flask(__name__,
            static_folder=os.path.join(os.path.dirname(__file__), 'static'),
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

app.secret_key = os.environ.get('SECRET_KEY', 'foodguard-secret-key-2026-do-not-use-in-production')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# ============================================================
# Business Layer Instances
# ============================================================
account_bus = AccountBUS()
allergen_bus = AllergenCheckerBUS()
ingredient_dao = IngredientDAO()
history_dao = HistoryDAO()

# Current scanned product (shared state for camera stream)
current_product = {
    "barcode": None,
    "name": None,
    "category": None,
    "ingredients": [],
    "warning_level": None,
    "warning_message": None,
    "matched_allergens": []
}

# ============================================================
# Business Layer Instances
# ============================================================
account_bus = AccountBUS()
allergen_bus = AllergenCheckerBUS()
ingredient_dao = IngredientDAO()
history_dao = HistoryDAO()

# Current scanned product (shared state for camera stream)
current_product = {
    "barcode": None,
    "name": None,
    "category": None,
    "ingredients": [],
    "warning_level": None,
    "warning_message": None,
    "matched_allergens": []
}

# --- CHÈN THÊM 2 DÒNG NÀY ĐỂ TẠO KHÓA CHẶN CAMERA ---
import threading

is_processing = False
processing_lock = threading.Lock()


# ============================================================
# Decorators
# ============================================================
def login_required(f):
    """Decorator kiểm tra user đã đăng nhập chưa."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập để tiếp tục.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated


# ============================================================
# Barcode Processing (THAY THẾ TOÀN BỘ HÀM NÀY)
# ============================================================
def process_barcode(barcode_val):
    global current_product, is_processing

    # 1. Xóa khoảng trắng thừa của mã vạch để tránh lệch dữ liệu SQL
    barcode_val = str(barcode_val).strip()

    # 2. Nếu mã vạch trùng với sản phẩm đang xử lý/hiển thị thì bỏ qua
    if barcode_val == current_product["barcode"] and current_product["name"] not in [None, "Đang tải..."]:
        return

    # 3. Khóa luồng: Nếu camera đang bận xử lý frame trước thì frame này bỏ qua
    with processing_lock:
        if is_processing:
            return
        is_processing = True

    try:
        print(f"\n[WEB APP] ---> Bắt đầu kiểm tra mã vạch: {barcode_val}")

        temp_product = {
            "barcode": barcode_val,
            "name": "Đang tải...",
            "category": "Đang tải...",
            "ingredients": [],
            "warning_level": None,
            "warning_message": None,
            "matched_allergens": []
        }

        # 4. Kiểm tra trong Database trước
        db_rows = get_product_details(barcode_val)
        print(f"[WEB APP] Kết quả từ Database: {db_rows}")

        if db_rows:
            print("[WEB APP] -> TÌM THẤY TRONG DATABASE! Không dùng API.")
            temp_product["name"] = db_rows[0][1]
            temp_product["category"] = db_rows[0][2]
            temp_product["ingredients"] = [item[3] for item in db_rows]
        else:
            print("[WEB APP] -> Không thấy trong DB. Tiến hành gọi API OpenFoodFacts...")
            food = get_product_from_openfoodfacts(barcode_val)
            if food:
                temp_product["name"] = food["name"]
                temp_product["category"] = food["category"]
                temp_product["ingredients"] = food["ingredients"]
            else:
                temp_product["name"] = "Không tìm thấy"
                temp_product["category"] = "Không tìm thấy"
                temp_product["ingredients"] = []

        current_product = temp_product

    except Exception as e:
        print(f"[WEB APP ERROR] Lỗi: {e}")
    finally:
        # 5. Xử lý xong hoàn toàn mới mở khóa cho frame tiếp theo vào
        is_processing = False
    if db_rows:
        temp_product["name"] = db_rows[0][1]
        temp_product["category"] = db_rows[0][2]
        temp_product["ingredients"] = [item[3] for item in db_rows]
    else:
        food = get_product_from_openfoodfacts(barcode_val)
        if food:
            temp_product["name"] = food["name"]
            temp_product["category"] = food["category"]
            temp_product["ingredients"] = food["ingredients"]
        else:
            temp_product["name"] = "Không tìm thấy"
            temp_product["category"] = "Không tìm thấy"
            temp_product["ingredients"] = []

    current_product = temp_product


def check_allergens_for_current_user(user_id, barcode_val):
    """
    Kiểm tra dị ứng cho user hiện tại và cập nhật current_product.
    """
    global current_product

    result = allergen_bus.check_allergens_by_barcode(user_id, barcode_val)

    current_product["warning_level"] = result.warning_level
    current_product["warning_message"] = result.warning_message
    current_product["matched_allergens"] = result.matched_allergens

    # Lưu lịch sử quét
    product_name = current_product.get("name", "Không xác định")
    history_dao.add_scan_record(user_id, barcode_val, product_name, result.warning_level)


# ============================================================
# Camera Stream
# ============================================================
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


# ============================================================
# Routes — Authentication
# ============================================================
@app.route('/')
def index():
    """Redirect về scanner nếu đã đăng nhập, hoặc login."""
    if 'user_id' in session:
        return redirect(url_for('scanner_page'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Trang đăng nhập bằng số điện thoại."""
    if 'user_id' in session:
        return redirect(url_for('scanner_page'))

    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()

        if not phone or not password:
            flash('Vui lòng nhập đầy đủ thông tin!', 'error')
            return render_template('login.html')

        try:
            success, message, user_id = account_bus.login_by_phone(phone, password)

            if success:
                # Lưu session
                user_info = account_bus.dao.get_account_by_id(user_id)
                session['user_id'] = user_id
                session['user_name'] = user_info.user_name
                session['phone'] = user_info.phone_number

                flash(f'Chào mừng {user_info.user_name}! 🎉', 'success')
                return redirect(url_for('scanner_page'))
            else:
                flash('Sai số điện thoại hoặc mật khẩu!', 'error')
        except Exception as e:
            print(f"[Login Error] {e}")
            flash('Không thể kết nối đến cơ sở dữ liệu. Vui lòng thử lại sau!', 'error')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Trang đăng ký tài khoản mới."""
    if 'user_id' in session:
        return redirect(url_for('scanner_page'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # Validate confirm password
        if password != confirm_password:
            flash('Mật khẩu xác nhận không khớp!', 'error')
            return render_template('register.html')

        try:
            success, message = account_bus.register_by_phone(name, phone, password)

            if success:
                flash(message, 'success')
                return redirect(url_for('login'))
            else:
                flash(message, 'error')
        except Exception as e:
            print(f"[Register Error] {e}")
            flash('Không thể kết nối đến cơ sở dữ liệu. Vui lòng thử lại sau!', 'error')

    return render_template('register.html')


@app.route('/logout')
def logout():
    """Đăng xuất — xóa session."""
    session.clear()
    flash('Đã đăng xuất thành công.', 'info')
    return redirect(url_for('login'))


# ============================================================
# Routes — Main Pages (require login)
# ============================================================
@app.route('/scanner')
@login_required
def scanner_page():
    """Trang quét mã vạch sản phẩm."""
    return render_template('scanner.html')


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_page():
    """Trang hồ sơ cá nhân + quản lý dị ứng."""
    user_id = session['user_id']

    if request.method == 'POST':
        new_name = request.form.get('user_name', '').strip()
        allergies_str = request.form.get('allergies', '').strip()

        # Parse danh sách dị ứng từ comma-separated string
        allergy_list = [a.strip() for a in allergies_str.split(',') if a.strip()]

        try:
            success, message = account_bus.update_profile_web(user_id, new_name, allergy_list)

            if success:
                # Cập nhật session name
                profile = account_bus.get_user_profile(user_id)
                if profile:
                    session['user_name'] = profile['user_name']
                flash(message, 'success')
            else:
                flash(message, 'error')
        except Exception as e:
            print(f"[Profile Update Error] {e}")
            flash('Không thể kết nối đến cơ sở dữ liệu. Vui lòng thử lại sau!', 'error')

        return redirect(url_for('profile_page'))

    # GET — load profile
    try:
        profile = account_bus.get_user_profile(user_id)
        scan_count = len(history_dao.get_user_history(user_id, limit=1000))
    except Exception as e:
        print(f"[Profile Load Error] {e}")
        flash('Không thể tải hồ sơ. Vui lòng thử lại sau!', 'error')
        profile = None
        scan_count = 0

    return render_template('profile.html', profile=profile, scan_count=scan_count)


@app.route('/history')
@login_required
def history_page():
    """Trang lịch sử quét sản phẩm."""
    user_id = session['user_id']
    history = history_dao.get_user_history(user_id, limit=50)
    return render_template('history.html', history=history)


# ============================================================
# API Routes
# ============================================================
@app.route('/video_feed')
@login_required
def video_feed():
    """Stream camera feed."""
    return Response(generate_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/get_data')
@login_required
def get_data():
    """
    API lấy dữ liệu sản phẩm hiện tại + kết quả kiểm tra dị ứng.
    """
    global current_product

    if current_product["barcode"] and current_product["warning_level"] is None:
        user_id = session.get('user_id')
        if user_id:
            if current_product["name"] != "Không tìm thấy":

                result = allergen_bus._check_allergens(user_id, {
                    "id": current_product["barcode"],
                    "name": current_product["name"],
                    "group": current_product["category"]
                })

                current_product["warning_level"] = result.warning_level
                current_product["warning_message"] = result.warning_message
                current_product["matched_allergens"] = result.matched_allergens

                history_dao.add_scan_record(user_id, current_product["barcode"], current_product["name"],
                                            result.warning_level)
            else:
                current_product["warning_level"] = "NOT_FOUND"
                current_product[
                    "warning_message"] = f"Không tìm thấy sản phẩm với mã vạch: {current_product['barcode']}"

    return jsonify(current_product)


@app.route('/api/ingredients')
@login_required
def api_ingredients():
    """API lấy danh sách tất cả thành phần (cho autocomplete profile)."""
    try:
        ingredients = ingredient_dao.get_all_ingredients()
        names = [ing.ingredient_name for ing in ingredients]
        return jsonify({"ingredients": names})
    except Exception as e:
        return jsonify({"ingredients": [], "error": str(e)})


# ============================================================
# Entry Point
# ============================================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)