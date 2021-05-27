import socket
import time
import pickle

HEADERSIZE = 4069

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 5050))
s.listen(5)

def send(sock, m):
    msg = pickle.dumps(m)
    msg = bytes(f"{len(msg):<{HEADERSIZE}}", 'utf-8') + msg
    sock.send(msg)

while True:
    conn, addr = s.accept()
    print(f"conn from {addr}")
    
    d = {1: "HELLO", 2: "theRe"}
    msg = pickle.dumps(d)
    
    msg = bytes(f"{len(msg):<{HEADERSIZE}}", 'utf-8') + msg
    conn.send(msg)
    time.sleep(1)
    send(conn, "124576484568")
    time.sleep(1)
    send(conn, "sfse135n15n1")
    time.sleep(1)
    send(conn, "1412412412b4214b21b42156 m3q6b5yq3456 m3q6m3q6m34qm6")
    time.sleep(1)
    send(conn, "2313123v1312v76i7689e")
    time.sleep(1)
    send(conn, "%*!@#()%&*(!&@%_*()!@%_&*")
    time.sleep(1)
    send(conn, "214124124v")
