# Minigame Cờ Caro bằng Python

Đây là một dự án minigame Cờ Caro (Gomoku) đơn giản được xây dựng bằng Python. Trò chơi cho phép hai người chơi kết nối với nhau qua mạng (TCP/IP) và thi đấu trên một bàn cờ 15x15.

Tính năng chính
- Chơi 2 người (Multiplayer):** Hỗ trợ 2 người chơi kết nối qua mạng.
- Kiến trúc Client-Server:** Server xử lý logic và điều phối trận đấu.
- Hỗ trợ 2 Giao diện:** Cung cấp 2 kiểu client:
    * Giao diện Đồ họa (GUI) 2D bằng Pygame.
    * Giao diện Console (Terminal) cơ bản.
- Logic game cơ bản:** Phát hiện thắng (5 quân liên tiếp), kiểm tra nước đi hợp lệ.
- Phòng chờ đơn giản:** Server tự động ghép cặp 2 người chơi kết nối đầu tiên.

Kiến trúc hệ thống
- Hệ thống được xây dựng theo mô hình Client-Server:

`game_logic.py`**: Module lõi chứa toàn bộ logic của trò chơi (tạo bàn cờ, kiểm tra nước đi, phát hiện thắng/thua).
`server.py`**: Máy chủ của trò chơi (lắng nghe kết nối, quản lý phòng chờ, điều phối ván đấu).
`client_gui.py`**: **Giao diện người chơi chính (GUI)**.
 * Sử dụng **Pygame** để vẽ bàn cờ, xử lý click chuột.
 * Sử dụng **đa luồng (threading)** để xử lý mạng ngầm, đảm bảo GUI không bị "treo".
`client_console.py`** (hoặc `client.py`): **Giao diện người chơi phụ (Console)**.
 * Hiển thị bàn cờ bằng text trong terminal.
 * Đã được vá lỗi (fix bugs) và cải tiến (xóa màn hình, thông báo tiếng Anh).
 * Hữu ích cho việc gỡ lỗi (debug) và kiểm thử (testing).

Cài đặt
1.  Yêu cầu Python 3:** Đảm bảo bạn đã cài đặt Python 3.
2.  Clone Repository:**
    git clone [https://github.com/THUYNGOC-LTN/MinigameCaro_GiuaKy.git]
    cd [./MinigameCaro_GiuaKy\MinigameCaro]
3.  Cài đặt Pygame:** Giao diện GUI yêu cầu thư viện `pygame`. Chạy lệnh sau trong terminal:
    pip install pygame
    *(Nếu lệnh `pip` bị lỗi, hãy thử: `python -m pip install pygame`)*


Hướng dẫn chạy
- Bạn sẽ cần mở 3 cửa sổ terminal (1 cho Server, 2 cho 2 Người chơi).
- Bước 1: Chạy Server (Terminal 1): python server.py 12347
Đây là bước bắt buộc. Server sẽ lắng nghe kết nối.
(Server sẽ bắt đầu ở cổng 12347 và chờ người chơi...)

- Bước 2: Chọn cách chơi
Bạn có thể chọn chơi bằng GUI (khuyến nghị) hoặc Console (để test).

+ Cách 1: Chơi bằng Giao diện Đồ họa (GUI)
- Cách này sẽ mở ra cửa sổ game 2D.
- Chạy Người chơi 1 (Terminal 2): python client_gui.py 127.0.0.1 12347
- Chạy Người chơi 2 (Terminal 3): python client_gui.py 127.0.0.1 12347
(Ngay khi người chơi 2 kết nối, hai cửa sổ game Pygame sẽ được kích hoạt và trận đấu bắt đầu.)

+ Cách 2: Chơi bằng Giao diện Console (Terminal)
- Cách này dùng để chơi hoặc kiểm thử (test) ngay trên terminal.
- Chạy Người chơi 1 (Terminal 2): python client.py 127.0.0.1 12347
Chạy Người chơi 2 (Terminal 3): python client.py 127.0.0.1 12347

Thành viên nhóm dự án:
1. Huỳnh Trọng Phúc - Server Developer
2. Tạ Đức Bảo - Client Developer
3. Lâm Thúy Ngọc - Game Logic & Kiểm tra thắng
4. Nguyễn Huỳnh Nhật Minh - Tester, Fix bugs, GUI, Documentation
