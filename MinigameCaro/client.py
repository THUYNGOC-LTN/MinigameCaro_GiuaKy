# client.py
import socket
import sys
import os 

def clear_screen():
    """Clears the terminal screen."""
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

def print_board(board):
    """Prints the 2D board list to the console beautifully."""
    size = len(board)
    header = "   " + " ".join([f"{i:<2}" for i in range(size)])
    print(header)
    
    for r_idx, row in enumerate(board):
        print(f"{r_idx:<2} " + " ".join(row))

def redraw_screen(board, message=""):
    """Clears the screen and redraws the entire UI."""
    clear_screen()
    print("--- WELCOME TO GOMOKU (CARO) ---")
    if message:
        print(f"\n[STATUS]: {message}\n")
    else:
        print("\n") 
    
    print_board(board)
    print("\n") 

def get_move_and_send(s, board, my_symbol):
    """
    Loops until the user enters valid syntax AND valid board coordinates.
    """
    size = len(board) 
    
    while True:
        try:
            move = input("Enter move (row col): ")
            x, y = map(int, move.strip().split())

            if not (0 <= x < size and 0 <= y < size):
                print(f"[INPUT ERROR]: Coordinates must be between 0 and {size-1}. Try again.")
                continue 

            previous_value = board[x][y]

            if previous_value != '.':
                print("[INPUT ERROR]: Cell is already occupied. Try again.")
                continue

            # Send move to server
            s.sendall(f"MOVE {x} {y}\n".encode())
            
            # Optimistic update
            board[x][y] = my_symbol
            
            return x, y, previous_value 
        
        except ValueError: 
            print("[INPUT ERROR]: Please enter two NUMBERS separated by a space. Try again.")


def main():
    if len(sys.argv) != 3:
        print("Usage: python client.py <host> <port>")
        return

    host = sys.argv[1]
    port = int(sys.argv[2])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    my_symbol = None
    board = [['.' for _ in range(15)] for _ in range(15)]
    last_move_info = None
    
    status_message = "Connecting to server..." 

    try:
        while True:
            data = s.recv(1024).decode().strip()
            if not data:
                print("Disconnected from server.")
                break

            for line in data.split('\n'):
                parts = line.strip().split()
                if not parts:
                    continue

                cmd = parts[0]

                if cmd == "START":
                    my_symbol = parts[1]
                    status_message = f"Game started! You are '{my_symbol}'."
                    redraw_screen(board, status_message) 

                elif cmd == "YOUR":
                    status_message = "It's your turn."
                    redraw_screen(board, status_message) 
                    
                    last_move_info = get_move_and_send(s, board, my_symbol)
                    
                    status_message = "Move sent, waiting for opponent..."
                    redraw_screen(board, status_message) 

                elif cmd == "OPPONENT":
                    x, y = int(parts[1]), int(parts[2])
                    opp_symbol = 'O' if my_symbol == 'X' else 'X'
                    board[x][y] = opp_symbol 
                    
                    status_message = f"Opponent moved to ({x}, {y})"
                    redraw_screen(board, status_message) 

                elif cmd == "INVALID":
                    invalid_reason = ' '.join(parts[1:])
                    
                    if last_move_info:
                        lx, ly, previous_value = last_move_info
                        board[lx][ly] = previous_value 
                        last_move_info = None
                    
                    status_message = f"Invalid move: {invalid_reason}. Your last move was reverted."
                    redraw_screen(board, status_message) 
                    
                    # Ask for input again immediately
                    status_message = "It's still your turn. Please enter a valid move."
                    print(f"\n[STATUS]: {status_message}\n") 
                    
                    last_move_info = get_move_and_send(s, board, my_symbol)
                    
                    status_message = "New move sent, waiting for opponent..."
                    redraw_screen(board, status_message) 

                elif cmd == "WIN":
                    clear_screen() 
                    print_board(board)
                    print("\n================\n    You win!    \n================\n")
                    return 

                elif cmd == "LOSE":
                    clear_screen() 
                    print_board(board)
                    print("\n================\n    You lose!   \n================\n")
                    return

                elif cmd == "DRAW":
                    clear_screen() 
                    print_board(board)
                    print("\n================\n  Game is a draw. \n================\n")
                    return

                elif cmd == "OPPONENT_LEFT":
                    clear_screen() 
                    print_board(board)
                    print("\n================\n Opponent disconnected. \n================\n")
                    return 
    
    except ConnectionAbortedError:
        print("Connection was aborted.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        s.close()

if __name__ == "__main__":
    main()