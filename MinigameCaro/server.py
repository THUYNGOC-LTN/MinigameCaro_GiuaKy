# server.py
import socket
import threading
import sys
from game_logic import Board, apply_move, check_win, is_full

HOST = '0.0.0.0'
PORT = 12345

clients_lock = threading.Lock()
waiting = []

def send(conn, msg):
    try:
        conn.sendall((msg + "\n").encode())
    except:
        pass

def recv(conn):
    try:
        data = conn.recv(1024)
        if not data:
            return None
        return data.decode().strip()
    except:
        return None

def handle_match(p1, p2):
    conn1, addr1 = p1
    conn2, addr2 = p2
    board = Board(size=15)
    symbols = {conn1: 'X', conn2: 'O'}
    players = [conn1, conn2]

    send(conn1, "START X")
    send(conn2, "START O")

    current = conn1
    other = conn2
    send(current, "YOUR TURN")

    while True:
        data = recv(current)
        if data is None:
            send(other, "OPPONENT_LEFT")
            break

        parts = data.split()
        if len(parts) >= 1 and parts[0] == "MOVE" and len(parts) == 3:
            try:
                x = int(parts[1])
                y = int(parts[2])
            except:
                send(current, "INVALID Invalid coordinates")
                continue

            sym = symbols[current]
            ok, reason = apply_move(board, x, y, sym)
            if not ok:
                send(current, f"INVALID {reason}")
                continue

            send(other, f"OPPONENT {x} {y}")

            if check_win(board, x, y):
                send(current, "WIN")
                send(other, "LOSE")
                break

            if is_full(board):
                send(current, "DRAW")
                send(other, "DRAW")
                break

            send(other, "YOUR TURN")
            current, other = other, current
        elif data == "EXIT":
            send(other, "OPPONENT_LEFT")
            break
        else:
            send(current, "INVALID Unknown command")

    conn1.close()
    conn2.close()

def client_thread(conn, addr):
    print(f"[+] Connected {addr}")
    with clients_lock:
        waiting.append((conn, addr))
        if len(waiting) >= 2:
            p1 = waiting.pop(0)
            p2 = waiting.pop(0)
            threading.Thread(target=handle_match, args=(p1, p2), daemon=True).start()

def main():
    global HOST, PORT
    if len(sys.argv) >= 2:
        PORT = int(sys.argv[1])

    print(f"Starting server on {HOST}:{PORT}")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)
    try:
        while True:
            conn, addr = s.accept()
            threading.Thread(target=client_thread, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("Shutting down server.")
    finally:
        s.close()

if __name__ == "__main__":
    main()
