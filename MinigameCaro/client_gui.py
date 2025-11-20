import socket
import sys
import threading
import pygame

# --- Game Settings ---
GRID_SIZE = 15
CELL_SIZE = 40
MARGIN = 20
INFO_HEIGHT = 60
SCREEN_WIDTH = GRID_SIZE * CELL_SIZE + MARGIN * 2
SCREEN_HEIGHT = GRID_SIZE * CELL_SIZE + MARGIN * 2 + INFO_HEIGHT

# --- Colors ---
COLOR_BACKGROUND = (255, 255, 255)
COLOR_GRID_LINES = (220, 220, 220)
COLOR_X = (70, 130, 200)
COLOR_O = (240, 100, 100)
COLOR_HIGHLIGHT = (255, 245, 180)
COLOR_TEXT = (80, 80, 80)
COLOR_INFO_BG = (245, 245, 245)

# --- Global State ---
board = [['.' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
my_symbol = None
is_my_turn = False
game_over = False
status_message = "Connecting..."
last_player_move = None
last_optimistic_move = None
sock = None 

# --- Drawing Functions ---

def draw_game(screen, font):
    """Draws the entire game interface."""
    # 1. Background
    screen.fill(COLOR_BACKGROUND)
    
    # 2. Highlight Last Move
    if last_player_move:
        r, c = last_player_move
        rect_x = MARGIN + c * CELL_SIZE
        rect_y = MARGIN + r * CELL_SIZE
        pygame.draw.rect(screen, COLOR_HIGHLIGHT, (rect_x, rect_y, CELL_SIZE, CELL_SIZE))

    # 3. Grid Lines
    for i in range(GRID_SIZE + 1):
        start_pos = (MARGIN + i * CELL_SIZE, MARGIN)
        end_pos = (MARGIN + i * CELL_SIZE, MARGIN + GRID_SIZE * CELL_SIZE)
        pygame.draw.line(screen, COLOR_GRID_LINES, start_pos, end_pos, 1)
        
        start_pos = (MARGIN, MARGIN + i * CELL_SIZE)
        end_pos = (MARGIN + GRID_SIZE * CELL_SIZE, MARGIN + i * CELL_SIZE)
        pygame.draw.line(screen, COLOR_GRID_LINES, start_pos, end_pos, 1)

    # 4. Pieces
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            center = (MARGIN + c * CELL_SIZE + CELL_SIZE // 2, 
                      MARGIN + r * CELL_SIZE + CELL_SIZE // 2)
            
            if board[r][c] == 'X':
                draw_X(screen, center)
            elif board[r][c] == 'O':
                draw_O(screen, center)

    # 5. Info Bar
    info_rect = (0, SCREEN_HEIGHT - INFO_HEIGHT, SCREEN_WIDTH, INFO_HEIGHT)
    pygame.draw.rect(screen, COLOR_INFO_BG, info_rect)
    pygame.draw.line(screen, COLOR_GRID_LINES, (0, SCREEN_HEIGHT - INFO_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT - INFO_HEIGHT), 1)
    
    text_surface = font.render(status_message, True, COLOR_TEXT)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - INFO_HEIGHT // 2))
    screen.blit(text_surface, text_rect)
    
    pygame.display.flip()

def draw_X(screen, center):
    offset = CELL_SIZE // 4
    start1 = (center[0] - offset, center[1] - offset)
    end1   = (center[0] + offset, center[1] + offset)
    pygame.draw.line(screen, COLOR_X, start1, end1, 5)
    
    start2 = (center[0] - offset, center[1] + offset)
    end2   = (center[0] + offset, center[1] - offset)
    pygame.draw.line(screen, COLOR_X, start2, end2, 5)

def draw_O(screen, center):
    radius = CELL_SIZE // 3 - 2
    pygame.draw.circle(screen, COLOR_O, center, radius, width=4) 

def pixel_to_grid(pos):
    x, y = pos
    if x < MARGIN or x > (SCREEN_WIDTH - MARGIN) or \
       y < MARGIN or y > (SCREEN_HEIGHT - INFO_HEIGHT - MARGIN):
        return None 
        
    row = (y - MARGIN) // CELL_SIZE
    col = (x - MARGIN) // CELL_SIZE
    return row, col

# --- Network Thread ---

def network_thread():
    global board, my_symbol, is_my_turn, game_over, status_message, last_optimistic_move, last_player_move

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
                    status_message = f"Start! You are '{my_symbol}'."
                
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
                
                elif cmd in ("WIN", "LOSE", "DRAW", "OPPONENT_LEFT"):
                    game_over = True
                    if cmd == "WIN": status_message = "VICTORY!"
                    if cmd == "LOSE": status_message = "DEFEAT!"
                    if cmd == "DRAW": status_message = "DRAW GAME."
                    if cmd == "OPPONENT_LEFT": status_message = "Opponent Left."

    except Exception as e:
        status_message = "Error connection."
        game_over = True

# --- Main Loop ---

def main():
    global sock, game_over, is_my_turn, status_message, last_optimistic_move, last_player_move
    
    if len(sys.argv) != 3:
        print("Usage: python client_gui.py <host> <port>")
        return

    host = sys.argv[1]
    port = int(sys.argv[2])

    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont('Segoe UI', 22, bold=True) 
    if not font: font = pygame.font.SysFont('Arial', 22, bold=True)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Caro Minimalist")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
    except Exception:
        status_message = "Cannot connect to server."
        game_over = True

    if not game_over:
        threading.Thread(target=network_thread, daemon=True).start()

    clock = pygame.time.Clock()
    
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if is_my_turn:
                    pos = pygame.mouse.get_pos()
                    grid_pos = pixel_to_grid(pos)
                    
                    if grid_pos:
                        r, c = grid_pos
                        if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and board[r][c] == '.':
                            board[r][c] = my_symbol
                            last_optimistic_move = (r, c)
                            last_player_move = (r, c)
                            sock.sendall(f"MOVE {r} {c}\n".encode())
                            is_my_turn = False
                            status_message = "Waiting..."

        draw_game(screen, font)
        clock.tick(60)

    draw_game(screen, font) 
    pygame.time.wait(3000)
    pygame.quit()
    if sock: sock.close()

if __name__ == "__main__":
    main()