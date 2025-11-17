# client_gui.py
import socket
import sys
import threading
import pygame

# --- Cài đặt Game ---
GRID_SIZE = 15
CELL_SIZE = 40  # Kích thước mỗi ô cờ (pixel)
MARGIN = 20     # Lề
INFO_HEIGHT = 80 # Khu vực hiển thị thông báo
SCREEN_WIDTH = GRID_SIZE * CELL_SIZE + MARGIN * 2
SCREEN_HEIGHT = GRID_SIZE * CELL_SIZE + MARGIN * 2 + INFO_HEIGHT

# --- Màu sắc ---
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRID = (50, 50, 50)
COLOR_X = (200, 0, 0)
COLOR_O = (0, 0, 200)

# --- Biến Toàn cục (Global State) ---
board = [['.' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
my_symbol = None
is_my_turn = False
game_over = False
status_message = "Connecting..."
last_move = None # Nước đi cuối cùng (để hoàn tác nếu server báo lỗi)
sock = None # Socket kết nối

# --- Hàm vẽ (Drawing Functions) ---

def draw_game(screen, font):
    """Vẽ toàn bộ giao diện game (nền, lưới, quân cờ, thông báo)."""
    # 1. Nền
    screen.fill(COLOR_WHITE)
    
    # 2. Vẽ lưới (Grid)
    for i in range(GRID_SIZE + 1):
        # Đường dọc
        start_pos = (MARGIN + i * CELL_SIZE, MARGIN)
        end_pos = (MARGIN + i * CELL_SIZE, MARGIN + GRID_SIZE * CELL_SIZE)
        pygame.draw.line(screen, COLOR_GRID, start_pos, end_pos)
        # Đường ngang
        start_pos = (MARGIN, MARGIN + i * CELL_SIZE)
        end_pos = (MARGIN + GRID_SIZE * CELL_SIZE, MARGIN + i * CELL_SIZE)
        pygame.draw.line(screen, COLOR_GRID, start_pos, end_pos)

    # 3. Vẽ quân cờ (X và O)
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            center = (MARGIN + c * CELL_SIZE + CELL_SIZE // 2, 
                      MARGIN + r * CELL_SIZE + CELL_SIZE // 2)
            if board[r][c] == 'X':
                draw_X(screen, center)
            elif board[r][c] == 'O':
                draw_O(screen, center)

    # 4. Vẽ khu vực thông báo
    info_rect = (0, SCREEN_HEIGHT - INFO_HEIGHT, SCREEN_WIDTH, INFO_HEIGHT)
    pygame.draw.rect(screen, COLOR_BLACK, info_rect)
    
    text = font.render(status_message, True, COLOR_WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - INFO_HEIGHT // 2))
    screen.blit(text, text_rect)
    
    # Cập nhật màn hình
    pygame.display.flip()

def draw_X(screen, center):
    """Vẽ 1 dấu X."""
    s = CELL_SIZE // 3 # Kích thước của dấu X
    pygame.draw.line(screen, COLOR_X, (center[0] - s, center[1] - s), (center[0] + s, center[1] + s), 4)
    pygame.draw.line(screen, COLOR_X, (center[0] - s, center[1] + s), (center[0] + s, center[1] - s), 4)

def draw_O(screen, center):
    """Vẽ 1 dấu O."""
    pygame.draw.circle(screen, COLOR_O, center, CELL_SIZE // 3, 4)

def pixel_to_grid(pos):
    """Chuyển đổi tọa độ pixel (click) sang tọa độ ô (row, col)."""
    x, y = pos
    if x < MARGIN or x > (SCREEN_WIDTH - MARGIN) or \
       y < MARGIN or y > (SCREEN_HEIGHT - INFO_HEIGHT - MARGIN):
        return None # Click ngoài bàn cờ
        
    row = (y - MARGIN) // CELL_SIZE
    col = (x - MARGIN) // CELL_SIZE
    return row, col

# --- Luồng Mạng (Network Thread) ---

def network_thread():
    """Luồng này lắng nghe tin nhắn từ server và cập nhật Global State."""
    global board, my_symbol, is_my_turn, game_over, status_message, last_move

    try:
        while not game_over:
            data = sock.recv(1024).decode().strip()
            if not data:
                status_message = "Disconnected from server."
                game_over = True
                break

            for line in data.split('\n'):
                parts = line.strip().split()
                if not parts: continue
                
                cmd = parts[0]

                if cmd == "START":
                    my_symbol = parts[1]
                    status_message = f"Game started! You are '{my_symbol}'."
                
                elif cmd == "YOUR":
                    is_my_turn = True
                    status_message = "Your turn."
                
                elif cmd == "OPPONENT":
                    r, c = int(parts[1]), int(parts[2])
                    opp_symbol = 'O' if my_symbol == 'X' else 'X'
                    board[r][c] = opp_symbol
                    status_message = f"Opponent moved to ({r}, {c})"
                
                elif cmd == "INVALID":
                    reason = ' '.join(parts[1:])
                    status_message = f"Invalid move: {reason}. Try again."
                    
                    # Hoàn tác (revert) nước đi "lạc quan"
                    if last_move:
                        r, c = last_move
                        board[r][c] = '.' # Trả lại ô trống
                        last_move = None
                    is_my_turn = True # Trả lại lượt
                
                elif cmd in ("WIN", "LOSE", "DRAW", "OPPONENT_LEFT"):
                    game_over = True
                    if cmd == "WIN": status_message = "You win!"
                    if cmd == "LOSE": status_message = "You lose!"
                    if cmd == "DRAW": status_message = "Game is a draw."
                    if cmd == "OPPONENT_LEFT": status_message = "Opponent disconnected."

    except Exception as e:
        status_message = f"Network error: {e}"
        game_over = True

# --- Luồng Chính (Main Thread / Game Loop) ---

def main():
    global sock, game_over, is_my_turn, status_message, last_move
    
    if len(sys.argv) != 3:
        print("Usage: python client_gui.py <host> <port>")
        return

    host = sys.argv[1]
    port = int(sys.argv[2])

    # Khởi tạo Pygame
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Caro (Gomoku)")
    font = pygame.font.SysFont('Arial', 24)

    # Kết nối mạng
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
    except Exception as e:
        status_message = f"Failed to connect: {e}"
        game_over = True

    # Khởi động luồng mạng
    if not game_over:
        threading.Thread(target=network_thread, daemon=True).start()

    # Vòng lặp chính của Game
    clock = pygame.time.Clock()
    while not game_over:
        
        # Xử lý Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            
            # Xử lý click chuột
            if event.type == pygame.MOUSEBUTTONDOWN:
                if is_my_turn:
                    pos = pygame.mouse.get_pos()
                    grid_pos = pixel_to_grid(pos)
                    
                    if grid_pos:
                        r, c = grid_pos
                        if board[r][c] == '.':
                            # Cập nhật "lạc quan" (Optimistic Update)
                            board[r][c] = my_symbol
                            last_move = (r, c)
                            
                            # Gửi nước đi
                            sock.sendall(f"MOVE {r} {c}\n".encode())
                            is_my_turn = False
                            status_message = "Move sent, waiting..."
                        else:
                            status_message = "Cell is already occupied."
                    else:
                        status_message = "Clicked outside the board."
                else:
                    status_message = "Please wait, not your turn."

        # Vẽ lại màn hình
        draw_game(screen, font)
        
        # Giới hạn 30 FPS
        clock.tick(30)

    draw_game(screen, font)

    # Giữ cửa sổ 5 giây trước khi thoát
    pygame.time.wait(5000)
    pygame.quit()
    if sock:
        sock.close()

if __name__ == "__main__":
    main()