import socket
import time
import pickle

HEADERSIZE = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 5050))
s.listen(5)


while True:
    conn, addr = s.accept()
    print(f"conn from {addr}")
    
    d = {1: "HELLO", 2: "theRe"}
    msg = pickle.dumps(d)
    
    msg = bytes(f"{len(msg):<{HEADERSIZE}}", 'utf-8') + msg
    conn.send(msg)
