import blockchain
import threading, socket, pickle, time  # All part of Python standard libary
socket.setdefaulttimeout(5)  # So socket.listen and socket.recv only run for 3 seconds to prevent program hanging

# These are commands we may receive
DISCONNECT_MESSAGE = '!DISCONNECT'  # A connection is disconnected
STATUS_MESSAGE = '!STATUS'  # Just to check for a connection
SEND_CHAIN_MESSAGE = '!GIVECHAIN'  # We send this if we want the chain, if we receive this we send the chain

class BlockchainNetwork:
    def __init__(self):
        self.ledger = blockchain.Blockchain()
        self.HEADER = 4069  # Expected file receive size, 4 kilobytes
        self.PORT = 5050  # The port in which we will be 'listening and talking' through
        self.MY_IP = socket.gethostbyname(socket.gethostname())  # find my local ip
        self.MY_ADDR = (self.MY_IP, self.PORT)
        self.run = True  # If the network should be active

        self.network_IPS = []
        with open("data/network_Ips.txt", "r") as r:
            for line in r.readlines():
                self.network_IPS.append(line.strip("\n"))
        # print(f"network ips: {self.network_IPS}")

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket obj for listening
        self.server.bind(self.MY_ADDR)  # 'Bind' it on this machine on port 5050
        self.clients = []  # Store all incoming sockets
        self.connections = []  # Store all outgoing sockets

    def send(self, conn, obj):
        time.sleep(3)
        dump = pickle.dumps(obj)
        msg = bytes(f'{len(dump):<{self.HEADER}}', 'utf-8') + dump
        conn.send(msg)

    def sendToIp(self, ip, obj):
        for conn in self.connections:
            if conn[1][0] == ip:
                self.send(conn[0], obj)
                return

    def sendAll(self, obj):
        for s in self.connections:
            print(f"[NET] sending {obj} to {s[1]}")
            self.send(s[0], obj)

    def handleReceive(self, msg):
        if type(msg) == blockchain.Identity:
            print("[NET] RECEIVED IDENTITY")
            self.ledger.add_identity(msg)
        elif type(msg) == blockchain.Block:
            print("[NET] RECEIVED BLOCK")
            self.ledger.add_block(msg)
        elif type(msg) == blockchain.Blockchain:
            print("[NET] RECEIVED CHAIN")
            if msg.check_integrity() != True:
                return
            if len(self.ledger.chain) > 1:
                if len(msg.chain) < len(self.ledger.chain):
                    return
                if msg.chain[0].cal_hash() != self.ledger.chain[0].cal_hash():
                    return
            self.ledger = msg

    def handleConn(self, conn, addr):
        print(f"\n[NET] new connection from {addr}")
        full_msg = b''
        new_msg = True
        while self.run:
            try:
                msg = conn.recv(self.HEADER)
                if new_msg:
                    print("new msg len:", msg[:self.HEADER])
                    msg_length = int(msg[:self.HEADER])
                    new_msg = False
                print(f"full msg length: {msg_length}")
                full_msg += msg
                print(len(full_msg))
                if len(full_msg)-self.HEADER == msg_length:
                    print("full msg recvd")
                    print(full_msg[self.HEADER:])
                    received_msg = pickle.loads(full_msg[self.HEADER:])
                    new_msg = True
                    full_msg = b''
                    print(f"[{addr}] received {received_msg}")

                    if received_msg == DISCONNECT_MESSAGE:
                        print(1)
                        self.close_connection(conn, addr)
                        break
                    if received_msg == STATUS_MESSAGE:
                        print(2)
                        self.sendToIp(addr[0], 'active')
                        continue
                    if received_msg == SEND_CHAIN_MESSAGE:
                        print(3)
                        self.sendToIp(addr[0], self.ledger)
                        continue
                    self.handleReceive(received_msg)
                    
            except socket.timeout:
                continue
            except ConnectionAbortedError as err:
                print(f"[{addr}] {err}")
                self.close_connection(conn, addr)
                break
            except ConnectionResetError as err:
                print(f"[{addr}] {err}")
                self.close_connection(conn, addr)
                break

    def listen(self):
        print(f"[NET] server listening on {self.server}")
        self.server.listen()
        while self.run:
            try:
                conn, addr = self.server.accept()  # socket.timeout is raise in 3 secs in no incoming conn
            except socket.timeout:  # socket.timeout so server.accept() doesnt run forever
                continue
            self.connect(addr[0])
            self.clients.append([conn, addr])  # then append a ptr of the socket to clients
            thread = threading.Thread(target=self.handleConn, args=(conn, addr))  # We got a new conn, so we handle it on a seprate thread
            thread.start()

    def connect(self, ip):
        for conn in self.connections:
            if conn[1][0] == ip:
                print("Already connected")
                return
        try:
            addr = (ip, self.PORT)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"[NET] connecting to {addr}...")
            s.connect(addr)
            print(f"[NET] connected to {addr}")
            self.connections.append([s, addr])
            print(self.connections)
        except socket.timeout:
            print(f"[NET] conn to {ip} timed out")
            pass
        except ConnectionRefusedError:
            print(f"[NET] {ip} refuesed to connect")
            pass

    def connectToNetwork(self):
        for ip in self.network_IPS:
            if ip == self.MY_IP:
                continue
            self.connect(ip)
    
    def close_connection(self, conn, addr):
        for i, conn in enumerate(self.connections):
            if conn[1][0] == addr[0]:
                # print(f"[NET] closing outgoing {self.connections[i]}")
                conn[0].close()
                self.connections.pop(i)
        for i, conn in enumerate(self.clients):
            if conn[1][0] == addr[0]:
                # print(f"[NET] closing incoming {self.clients[i]}")
                conn[0].close()
                self.clients.pop(i)

    def createIdentity(self, name, face_encoding):
        iden, qk, pk = self.ledger.create_identity(name, face_encoding)
        self.sendAll(iden)
        with open("data/keys.txt", "a+") as r:
            r.write(f"{name} {qk} {pk}\n")
        return qk, pk

    def mineBlock(self):
        block = self.ledger.mine_block()
        self.sendAll(block)

    def get_conns(self):
        conns = []
        for conn in self.connections:
            conns.append(conn[1])
        return conns

    def get_faces(self):
        return self.ledger.get_all_faces()

    def start(self):
        # to start the network we create a listen thread for incoming connections
        thread = threading.Thread(target=self.listen)
        thread.start()
        time.sleep(3)
        self.connectToNetwork()

    def close(self):
        self.sendAll(DISCONNECT_MESSAGE)  # Not send to network because we only need to disconnect from current conns
        self.run = False
        self.ledger.save()
