# client.py
import socket
import threading
import sys
from game_logic import Board, board_to_string, apply_move

HOST = '127.0.0.1'
PORT = 12345

def send(sock, msg):
    try:
        sock.sendall((msg + "\n").encode())
    except:
        pass

def recv(sock):
    try:
        data = sock.recv(1024)
        if not data:
            return None
        return data.decode().strip()
    except:
        return None

def listen_thread(sock, board_state):
    while True:
        data = recv(sock)
        if data is None:
            print("[!] Disconnected from server.")
            break
        for line in data.splitlines():
            parts = line.split()
            if not parts:
                continue
            cmd = parts[0]
            if cmd == "START":
                symbol = parts[1] if len(parts) > 1 else '?'
                print(f"[+] Game started. You are: {symbol}")
                board_state['symbol'] = symbol
            elif cmd == "YOUR":
                print("[*] It's your turn. Enter move as: row col (0-14)")
                board_state['your_turn'] = True
            elif cmd == "OPPONENT":
                if len(parts) >= 3:
                    x = int(parts[1]); y = int(parts[2])
                    opp_sym = 'O' if board_state.get('symbol') == 'X' else 'X'
                    apply_move(board_state['board'], x, y, opp_sym)
                    print(f"[>] Opponent moved: {x} {y}")
                    print(board_to_string(board_state['board']))
                else:
                    print("[!] Malformed OPPONENT message")
            elif cmd == "WIN":
                print("[!!!] You WIN 🎉")
                return
            elif cmd == "LOSE":
                print("[xxx] You LOSE")
                return
            elif cmd == "DRAW":
                print("[=] Draw")
                return
            elif cmd == "INVALID":
                reason = " ".join(parts[1:]) if len(parts) > 1 else ""
                print(f"[!] Invalid move: {reason}")
                board_state['your_turn'] = True
            elif cmd == "OPPONENT_LEFT":
                print("[!] Opponent left the game.")
                return
            else:
                print(f"[?] Unknown message from server: {line}")

def main():
    global HOST, PORT
    if len(sys.argv) >= 2:
        HOST = sys.argv[1]
    if len(sys.argv) >= 3:
        PORT = int(sys.argv[2])

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except Exception as e:
        print("Could not connect to server:", e)
        return

    from game_logic import Board
    board_state = {'board': Board(15), 'symbol': None, 'your_turn': False}

    t = threading.Thread(target=listen_thread, args=(sock, board_state), daemon=True)
    t.start()

    try:
        while True:
            if board_state.get('your_turn'):
                raw = input("Enter your move (row col) or 'exit': ").strip()
                if raw.lower() in ('exit','quit'):
                    send(sock, "EXIT")
                    break
                parts = raw.split()
                if len(parts) != 2:
                    print("Invalid input. Use: row col (e.g. 7 8)")
                    continue
                try:
                    x = int(parts[0]); y = int(parts[1])
                except:
                    print("Invalid numbers.")
                    continue
                apply_move(board_state['board'], x, y, board_state['symbol'] or 'X')
                print(board_to_string(board_state['board']))
                send(sock, f"MOVE {x} {y}")
                board_state['your_turn'] = False
    except KeyboardInterrupt:
        send(sock, "EXIT")
    finally:
        sock.close()
        print("Client exiting.")

if __name__ == "__main__":
    main()
