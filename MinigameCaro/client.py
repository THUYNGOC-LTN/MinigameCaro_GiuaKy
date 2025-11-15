# client.py
import socket
import sys

def print_board(board_str):
    print(board_str)

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
                print(f"Game started! You are '{my_symbol}'.")

            elif cmd == "YOUR":
                print("It's your turn.")
                while True:
                    try:
                        move = input("Enter move (row col): ")
                        x, y = map(int, move.strip().split())
                        s.sendall(f"MOVE {x} {y}\n".encode())
                        break
                    except Exception as e:
                        print("Invalid input. Please enter two numbers separated by space.")

            elif cmd == "OPPONENT":
                x, y = int(parts[1]), int(parts[2])
                opp_symbol = 'O' if my_symbol == 'X' else 'X'
                board[x][y] = opp_symbol
                print(f"Opponent moved to ({x}, {y})")

            elif cmd == "INVALID":
                print("Invalid move:", ' '.join(parts[1:]))

            elif cmd == "WIN":
                print("You win!")
                return

            elif cmd == "LOSE":
                print("You lose!")
                return

            elif cmd == "DRAW":
                print("Game is a draw.")
                return

            elif cmd == "OPPONENT_LEFT":
                print("Opponent disconnected.")
                return

    s.close()

if __name__ == "__main__":
    main()
