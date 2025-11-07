# game_logic.py
def Board(size=15):
    return [['.' for _ in range(size)] for _ in range(size)]

def in_bounds(size, x, y):
    return 0 <= x < size and 0 <= y < size

def apply_move(board, x, y, symbol):
    size = len(board)
    if not in_bounds(size, x, y):
        return False, "Out of bounds"
    if board[x][y] != '.':
        return False, "Cell occupied"
    board[x][y] = symbol
    return True, None

def _count_dir(board, x, y, dx, dy):
    size = len(board)
    sym = board[x][y]
    cnt = 0
    cx, cy = x + dx, y + dy
    while 0 <= cx < size and 0 <= cy < size and board[cx][cy] == sym:
        cnt += 1
        cx += dx
        cy += dy
    return cnt

def check_win(board, x, y):
    size = len(board)
    sym = board[x][y]
    if sym == '.':
        return False
    directions = [(0,1), (1,0), (1,1), (1,-1)]
    for dx, dy in directions:
        cnt = 1 + _count_dir(board, x, y, dx, dy) + _count_dir(board, x, y, -dx, -dy)
        if cnt >= 5:
            return True
    return False

def is_full(board):
    for row in board:
        if '.' in row:
            return False
    return True

def board_to_string(board):
    size = len(board)
    lines = ["   " + " ".join([f"{i:2}" for i in range(size)])]
    for i, row in enumerate(board):
        lines.append(f"{i:2} " + " ".join(row))
    return "\n".join(lines)
