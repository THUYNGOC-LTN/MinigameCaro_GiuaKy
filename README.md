# Minigame Cờ Caro bằng Python

Đây là một dự án minigame Cờ Caro (Gomoku) đơn giản được xây dựng bằng Python. Trò chơi cho phép hai người chơi kết nối với nhau qua mạng (TCP/IP) và thi đấu trên một bàn cờ 15x15.

## Tính năng chính

* **Chơi 2 người (Multiplayer):** Hỗ trợ 2 người chơi kết nối qua mạng.
* **Kiến trúc Client-Server:** Server xử lý logic và điều phối trận đấu.
* **Logic game cơ bản:** Phát hiện thắng (5 quân liên tiếp), kiểm tra nước đi hợp lệ (ô trống, trong bàn cờ).
* **Phòng chờ đơn giản:** Server tự động ghép cặp 2 người chơi kết nối đầu tiên.

## Kiến trúc hệ thống

Hệ thống được xây dựng theo mô hình Client-Server:

* **`game_logic.py`**: Module lõi chứa toàn bộ logic của trò chơi.
    * Tạo bàn cờ.
    * Kiểm tra tính hợp lệ của nước đi.
    * Phát hiện thắng/thua.
* **`server.py`**: Máy chủ của trò chơi.
    * Lắng nghe các kết nối từ client.
    * Quản lý phòng chờ (`waiting`) và ghép cặp 2 người chơi.
    * Điều phối lượt đi và truyền thông tin ván đấu (nước đi, thắng, thua, lỗi...) giữa 2 client.
* **`client.py`**: Giao diện người chơi.
    * Kết nối đến server.
    * Hiển thị bàn cờ.
    * Nhận input từ người dùng và gửi lên server.
    * Hiển thị thông báo từ server.

## Cài đặt

Dự án này được viết bằng Python thuần (sử dụng các thư viện chuẩn như `socket`, `threading`) và **không yêu cầu bất kỳ thư viện bên ngoài nào**.

Bạn chỉ cần có **Python 3** đã được cài đặt trên máy.

1.  Clone repository này về máy của bạn:
    ```bash
    git clone (https://github.com/THUYNGOC-LTN/MinigameCaro_GiuaKy.git)
    ```
2.  Di chuyển vào thư mục dự án:
    ```bash
    cd ..\MinigameCaro\MinigameCaro_GiuaKy\MinigameCaro
    ```

## Hướng dẫn chạy

Bạn sẽ cần mở **3 cửa sổ terminal** (hoặc CMD/PowerShell) để chạy trò chơi (1 cho Server, 2 cho 2 Người chơi).

1. Chạy Server (Terminal 1):
- Khởi động máy chủ. Bạn có thể chỉ định một cổng (port) tùy ý (ví dụ: `12347`). Gõ lệnh: python server.py 12347
- Server sẽ bắt đầu và hiển thị thông báo Starting server on 0.0.0.0:12347 và chờ người chơi...

2. Chạy Người chơi 1 (Terminal 2):
- Kết nối client đầu tiên vào server. Bạn cần cung cấp địa chỉ IP của server (nếu chạy trên cùng máy, dùng 127.0.0.1 hoặc localhost) và cổng 12347 đã thiết lập ở trên. Gõ lệnh: python client.py 127.0.0.1 12347
- Người chơi này sẽ kết nối và vào phòng chờ (sẽ được gán là 'X').

3. Chạy Người chơi 2 (Terminal 3):
- Kết nối client thứ hai theo cách tương tự. Gõ lệnh: python client.py 127.0.0.1 12347
- Ngay khi người chơi 2 kết nối, server sẽ ghép cặp cả hai và trận đấu sẽ tự động bắt đầu. Cả hai người chơi có thể bắt đầu thi đấu.

Thành viên nhóm dự án:
1. Huỳnh Trọng Phúc - Server Developer
2. Tạ Đức Bảo - Client Developer
3. Lâm Thúy Ngọc - Game Logic & Kiểm tra thắng
4. Nguyễn Huỳnh Nhật Minh - Tester & Documentation
