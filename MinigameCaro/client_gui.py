# client_gui.py
import socket
import sys
import threading
import pygame
import time

# --- Game Settings ---
GRID_SIZE = 15
CELL_SIZE = 40
MARGIN = 20
INFO_HEIGHT = 60
BOARD_WIDTH = GRID_SIZE * CELL_SIZE + MARGIN * 2
CHAT_WIDTH = 300
SCREEN_WIDTH = BOARD_WIDTH + CHAT_WIDTH
SCREEN_HEIGHT = GRID_SIZE * CELL_SIZE + MARGIN * 2 + INFO_HEIGHT

# --- Colors (GIỮ NGUYÊN STYLE MINIMALIST) ---
COLOR_BG = (255, 255, 255)          # Trắng tinh
COLOR_GRID = (220, 220, 220)        # Xám rất nhạt
COLOR_X = (70, 130, 200)            # Xanh dương dịu
COLOR_O = (240, 100, 100)           # Đỏ hồng (Salmon)
COLOR_HIGHLIGHT = (255, 245, 180)   # Vàng kem
COLOR_TEXT = (80, 80, 80)           # Xám đậm
COLOR_INFO_BG = (245, 245, 245)     # Nền thanh thông báo
COLOR_CHAT_BG = (240, 248, 255)     # Alice Blue
COLOR_INPUT_BG = (255, 255, 255)
COLOR_BORDER = (200, 200, 200)
# Màu nút bấm mới
COLOR_BTN_NORMAL = (100, 200, 100)  # Xanh lá
COLOR_BTN_HOVER = (120, 220, 120)   # Xanh lá sáng
COLOR_OVERLAY = (255, 255, 255, 200) # Lớp phủ trắng mờ khi hết game

# --- Global State ---
board = [['.' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
my_symbol = None
is_my_turn = False
game_over = False
status_message = "Connecting..."
last_player_move = None
last_optimistic_move = None
sock = None

# --- Rematch State (TÍNH NĂNG MỚI) ---
game_over_time = 0
rematch_sent = False
TIMEOUT_SECONDS = 15

# --- Chat State ---
chat_history = []
input_text = ""
MAX_CHAT_LINES = 18

# --- Drawing Functions ---

def draw_button(screen, font, rect, text, is_hover):
    """Vẽ nút bấm bo tròn."""
    color = COLOR_BTN_HOVER if is_hover else COLOR_BTN_NORMAL
    # Vẽ bóng đổ nhẹ
    pygame.draw.rect(screen, (200, 200, 200), (rect[0]+2, rect[1]+2, rect[2], rect[3]), border_radius=10)
    # Vẽ nút chính
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, COLOR_BORDER, rect, 2, border_radius=10)
    
    txt_surf = font.render(text, True, (255, 255, 255))
    txt_rect = txt_surf.get_rect(center=(rect[0] + rect[2]//2, rect[1] + rect[3]//2))
    screen.blit(txt_surf, txt_rect)

def draw_game(screen, font_game, font_chat):
    screen.fill(COLOR_BG)
    
    # --- 1. VẼ BÀN CỜ (Bên trái) ---
    # Highlight ô vừa đánh
    if last_player_move:
        r, c = last_player_move
        rect_x = MARGIN + c * CELL_SIZE
        rect_y = MARGIN + r * CELL_SIZE
        pygame.draw.rect(screen, COLOR_HIGHLIGHT, (rect_x, rect_y, CELL_SIZE, CELL_SIZE))

    # Vẽ lưới (mảnh mai)
    for i in range(GRID_SIZE + 1):
        start_pos = (MARGIN + i * CELL_SIZE, MARGIN)
        end_pos = (MARGIN + i * CELL_SIZE, MARGIN + GRID_SIZE * CELL_SIZE)
        pygame.draw.line(screen, COLOR_GRID, start_pos, end_pos, 1)
        
        start_pos = (MARGIN, MARGIN + i * CELL_SIZE)
        end_pos = (MARGIN + GRID_SIZE * CELL_SIZE, MARGIN + i * CELL_SIZE)
        pygame.draw.line(screen, COLOR_GRID, start_pos, end_pos, 1)

    # Vẽ quân cờ
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            center = (MARGIN + c * CELL_SIZE + CELL_SIZE // 2, 
                      MARGIN + r * CELL_SIZE + CELL_SIZE // 2)
            if board[r][c] == 'X': draw_X(screen, center)
            elif board[r][c] == 'O': draw_O(screen, center)

    # --- 2. THANH TRẠNG THÁI ---
    info_rect = (0, SCREEN_HEIGHT - INFO_HEIGHT, BOARD_WIDTH, INFO_HEIGHT)
    # Chỉ vẽ nền thanh trạng thái khi game chưa kết thúc (để không che nút Chơi lại)
    if not (game_over and not status_message.startswith("Opponent Left")):
        pygame.draw.rect(screen, COLOR_INFO_BG, info_rect)
    
    pygame.draw.line(screen, COLOR_GRID, (0, SCREEN_HEIGHT - INFO_HEIGHT), (BOARD_WIDTH, SCREEN_HEIGHT - INFO_HEIGHT), 1)
    
    text_surf = font_game.render(status_message, True, COLOR_TEXT)
    text_rect = text_surf.get_rect(center=(BOARD_WIDTH // 2, SCREEN_HEIGHT - INFO_HEIGHT // 2))
    screen.blit(text_surf, text_rect)

    # --- 3. KHUNG CHAT (Bên phải) ---
    chat_rect = (BOARD_WIDTH, 0, CHAT_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(screen, COLOR_CHAT_BG, chat_rect)
    pygame.draw.line(screen, COLOR_BORDER, (BOARD_WIDTH, 0), (BOARD_WIDTH, SCREEN_HEIGHT), 2)

    title_surf = font_game.render("CHAT ROOM", True, COLOR_X)
    screen.blit(title_surf, (BOARD_WIDTH + 20, 10))

    start_y = 50
    line_height = 25
    lines_to_show = chat_history[-MAX_CHAT_LINES:] 
    for i, line in enumerate(lines_to_show):
        color = COLOR_X if line.startswith("Me:") else (COLOR_O if line.startswith("Opp:") else COLOR_TEXT)
        txt_surf = font_chat.render(line, True, color)
        screen.blit(txt_surf, (BOARD_WIDTH + 10, start_y + i * line_height))

    input_rect = (BOARD_WIDTH + 10, SCREEN_HEIGHT - 40, CHAT_WIDTH - 20, 30)
    pygame.draw.rect(screen, COLOR_INPUT_BG, input_rect)
    pygame.draw.rect(screen, COLOR_BORDER, input_rect, 1)
    
    input_surf = font_chat.render(input_text, True, COLOR_TEXT)
    screen.blit(input_surf, (input_rect[0] + 5, input_rect[1] + 5))

    # --- 4. NÚT CHƠI LẠI (OVERLAY) ---
    if game_over and not status_message.startswith("Opponent Left"):
        # Tính thời gian còn lại
        elapsed = (pygame.time.get_ticks() - game_over_time) / 1000
        remaining = max(0, TIMEOUT_SECONDS - elapsed)
        
        if remaining > 0:
            # Lớp phủ mờ để làm nổi bật nút
            overlay = pygame.Surface((BOARD_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill(COLOR_OVERLAY)
            screen.blit(overlay, (0,0))

            # Vẽ nút
            btn_width, btn_height = 180, 60
            btn_x = (BOARD_WIDTH - btn_width) // 2
            btn_y = (SCREEN_HEIGHT - INFO_HEIGHT) // 2
            btn_rect = (btn_x, btn_y, btn_width, btn_height)
            
            mouse_pos = pygame.mouse.get_pos()
            is_hover = btn_rect[0] < mouse_pos[0] < btn_rect[0]+btn_width and \
                       btn_rect[1] < mouse_pos[1] < btn_rect[1]+btn_height
            
            label = "WAITING..." if rematch_sent else f"PLAY AGAIN ({int(remaining)})"
            draw_button(screen, font_game, btn_rect, label, is_hover)

    pygame.display.flip()

def draw_X(screen, center):
    """Vẽ X (Dày, gọn)"""
    offset = CELL_SIZE // 4
    start1 = (center[0] - offset, center[1] - offset)
    end1   = (center[0] + offset, center[1] + offset)
    pygame.draw.line(screen, COLOR_X, start1, end1, 5)
    start2 = (center[0] - offset, center[1] + offset)
    end2   = (center[0] + offset, center[1] - offset)
    pygame.draw.line(screen, COLOR_X, start2, end2, 5)

def draw_O(screen, center):
    """Vẽ O (Rỗng, giống cái nhẫn)"""
    radius = CELL_SIZE // 3 - 2
    # width=4 tạo vòng tròn rỗng
    pygame.draw.circle(screen, COLOR_O, center, radius, width=4) 

def pixel_to_grid(pos):
    x, y = pos
    if x > BOARD_WIDTH: return None 
    if x < MARGIN or x > (BOARD_WIDTH - MARGIN) or \
       y < MARGIN or y > (SCREEN_HEIGHT - INFO_HEIGHT - MARGIN):
        return None 
    row = (y - MARGIN) // CELL_SIZE
    col = (x - MARGIN) // CELL_SIZE
    return row, col

# --- Network Thread ---

def network_thread():
    global board, my_symbol, is_my_turn, game_over, status_message, last_optimistic_move, last_player_move, chat_history, game_over_time, rematch_sent

    try:
        while True:
            data = sock.recv(1024).decode().strip()
            if not data:
                status_message = "Disconnected."
                game_over = True
                break

            for line in data.split('\n'):
                parts = line.strip().split()
                if not parts: continue
                cmd = parts[0]

                if cmd == "START":
                    my_symbol = parts[1]
                    status_message = f"You are '{my_symbol}'."
                elif cmd == "YOUR":
                    is_my_turn = True
                    status_message = "Your Turn."
                elif cmd == "OPPONENT":
                    r, c = int(parts[1]), int(parts[2])
                    opp_symbol = 'O' if my_symbol == 'X' else 'X'
                    board[r][c] = opp_symbol
                    last_player_move = (r, c)
                    status_message = "Opponent moved."
                elif cmd == "INVALID":
                    status_message = "Invalid move!"
                    if last_optimistic_move: 
                        r, c = last_optimistic_move
                        board[r][c] = '.' 
                        last_optimistic_move = None
                    is_my_turn = True 
                elif cmd == "CHAT":
                    msg = " ".join(parts[1:])
                    chat_history.append(f"Opp: {msg}")
                
                # --- RESET GAME ---
                elif cmd == "RESET":
                    board = [['.' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
                    last_player_move = None
                    last_optimistic_move = None
                    rematch_sent = False
                    game_over = False
                    status_message = "New Game Started!"
                    chat_history.append("--- SYSTEM: NEW GAME ---")
                # ------------------

                elif cmd in ("WIN", "LOSE", "DRAW", "OPPONENT_LEFT"):
                    game_over = True
                    game_over_time = pygame.time.get_ticks()
                    if cmd == "WIN": status_message = "VICTORY!"
                    if cmd == "LOSE": status_message = "DEFEAT!"
                    if cmd == "DRAW": status_message = "DRAW GAME."
                    if cmd == "OPPONENT_LEFT": status_message = "Opponent Left."

    except Exception:
        status_message = "Error connection."
        game_over = True

# --- Main Loop ---

def main():
    global sock, game_over, is_my_turn, status_message, last_optimistic_move, last_player_move, input_text, chat_history, rematch_sent
    
    if len(sys.argv) != 3:
        print("Usage: python client_gui.py <host> <port>")
        return

    host = sys.argv[1]
    port = int(sys.argv[2])

    pygame.init()
    pygame.font.init()
    # Ưu tiên Font đẹp (Segoe UI)
    font_game = pygame.font.SysFont('Segoe UI', 22, bold=True) 
    if not font_game: font_game = pygame.font.SysFont('Arial', 22, bold=True)
    font_chat = pygame.font.SysFont('Arial', 16)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Caro Minimalist Rematch")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
    except Exception:
        status_message = "Cannot connect."
        game_over = True

    if not game_over:
        threading.Thread(target=network_thread, daemon=True).start()

    clock = pygame.time.Clock()
    running = True

    while running:
        current_time = pygame.time.get_ticks()
        
        # Timeout tự thoát nếu không Rematch
        if game_over and not status_message.startswith("Opponent Left"):
             elapsed = (current_time - game_over_time) / 1000
             if elapsed > TIMEOUT_SECONDS and not rematch_sent:
                 running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Chat input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if input_text.strip():
                        sock.sendall(f"CHAT {input_text}\n".encode())
                        chat_history.append(f"Me: {input_text}")
                        input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    if len(input_text) < 30:
                        input_text += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Xử lý nút Play Again
                if game_over and not rematch_sent:
                     btn_width, btn_height = 180, 60
                     btn_x = (BOARD_WIDTH - btn_width) // 2
                     btn_y = (SCREEN_HEIGHT - INFO_HEIGHT) // 2
                     if btn_x < event.pos[0] < btn_x + btn_width and \
                        btn_y < event.pos[1] < btn_y + btn_height:
                            sock.sendall("REMATCH\n".encode())
                            rematch_sent = True
                            chat_history.append("Me: Wants a rematch...")
                
                # Xử lý đánh cờ
                elif not game_over and event.pos[0] < BOARD_WIDTH: 
                    if is_my_turn:
                        grid_pos = pixel_to_grid(event.pos)
                        if grid_pos:
                            r, c = grid_pos
                            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and board[r][c] == '.':
                                board[r][c] = my_symbol
                                last_optimistic_move = (r, c)
                                last_player_move = (r, c)
                                sock.sendall(f"MOVE {r} {c}\n".encode())
                                is_my_turn = False
                                status_message = "Waiting..."

        draw_game(screen, font_game, font_chat)
        clock.tick(60)

    pygame.quit()
    if sock: sock.close()

if __name__ == "__main__":
    main()