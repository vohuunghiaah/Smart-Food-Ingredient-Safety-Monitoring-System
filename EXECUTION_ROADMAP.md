    task 1: Tuyen
    - xử lý đăng ký, đăng nhập tài khoản người dùng, đổi mật khẩu,...
    - thiết lập profile cho tài khoản bao gồm họ tên, sđt, các thành phần dị ứng của user
    lưu tất cả vào database
    task 2: Tien
    - xử lý quét, đọc mã vạch
    - viết hàm truy vấn trong database và trả về thông tin sản phẩm đó bao gồm:id, tên, nhóm sản phẩm, thành phần
    task 3: Nghia
    - xử lý phân loại cảnh báo: Nhận input là danh sách dị ứng của user và danh sách thành phần của sản phẩm vừa quét
        + nguy hiểm ( màu đỏ ) khi phát hiện chất dị ứng
        + cẩn thân ( màu vàng ) khi có thành phần liên quan đến chất dị ứng
        + an toàn ( màu xanh ) khi không phát hiện chất dị ứng
        các trường hợp đỏ và vàng thì cần in ra cụ thể là chất gì gây nguy hiểm
    - nếu sản phẩm cảnh báo nguy hiểm màu đỏ thì gọi hàm sản phẩm thanh thế để gợi ý 3 sản phẩm khác cùng nhóm và an toàn cho người dùng
    task 4: Thuy
    - thiết kế database, kết nối sql
    - huấn luyện máy học cho việc gợi ý sản phẩm thay thế
    - gộp code, viết main.py

Lưu ý: có thể thay đổi cải tiến để hệ thống chạy tốt hơn, dl 23h 26/05
