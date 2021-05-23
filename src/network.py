import blockchain
import threading, socket, pickle, time  # All part of Python standard libary
socket.setdefaulttimeout(3)  # So socket.listen and socket.recv only run for 3 seconds to prevent program hanging

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
        print(f"network ips: {self.network_IPS}")

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket obj for listening
        self.server.bind(self.MY_ADDR)  # 'Bind' it on this machine on port 5050
        self.clients = []  # Store all incoming sockets
        self.connections = []  # Store all outgoing sockets

    def send(self, conn, obj):
        """
        conn: Ptr of the socket obj we wish to send to
        obj: Object we wish to send
        """
        dump = pickle.dumps(obj)
        conn.sendall(dump)

    def sendAll(self, obj):
        dump = pickle.dumps(obj)
        for s in self.connections:
            s[0].sendall(dump)

    def handleReceive(self, receive):
        if type(receive) == blockchain.Identity:
            print("[NET] IDENTITY")
            self.ledger.add_identity(receive)
        if type(receive) == blockchain.Block:
            print("[NET] BLOCK")
            self.ledger.add_block(receive)
        if type(receive) == blockchain.Blockchain:
            print("[NET] CHAIN")
            if receive.check_integrity() != True:
                return
            if len(self.ledger.chain) > 1:
                if len(receive.chain) < len(self.ledger.chain):
                    return
                if receive.chain[0].cal_hash() != self.ledger.chain[0].cal_hash():
                    return
            self.ledger = receive

    def handleConn(self, conn, addr):
        print(f"\n[NET] new connection from {addr}")
        while self.run:
            try:
                receive = conn.recv(self.HEADER)
            except socket.timeout:
                continue
            except ConnectionResetError as err:
                print(f"[{addr}] {err}")
                conn.close()
                break
            except ConnectionAbortedError as err:
                print(f"[{addr}] {err}")
                conn.close()
                break

            if receive:
                receive = pickle.loads(receive)
                if receive == DISCONNECT_MESSAGE:
                    conn.close()
                    break
                if receive == STATUS_MESSAGE:
                    self.send(conn, True)
                    continue
                if receive == SEND_CHAIN_MESSAGE:
                    self.send(conn, self.ledger)
                    continue
                print(f"[{addr}] received {receive}")
                self.handleReceive(receive)
    
    def listen(self):
        print(f"[NET] server listening on {self.MY_ADDR}")
        self.server.listen()
        while self.run:            
            try:
                conn, addr = self.server.accept()  # socket.timeout is raise in 3 secs in no incoming conn
            except socket.timeout:  # socket.timeout so server.accept() doesnt run forever
                continue

            self.clients.append([conn, addr])  # then append a ptr of the socket to clients
            thread = threading.Thread(target=self.handleConn, args=(conn, addr))  # We got a new conn, so we handle it on a seprate thread
            thread.start()

    def connectToNetwork(self):
        for ip in self.network_IPS:
            if ip == self.MY_IP:
                break
            addr = (ip, self.PORT)
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(addr)
                print(f"[NET] connected to {addr}")
                self.connections.append([s, addr])
            except socket.timeout:
                print(f"[NET] conn to {ip} timed out")
            except ConnectionRefusedError:
                print(f"[NET] {ip} refuesed to connect")

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
        return self.clients

    def get_faces(self):
        return self.ledger.get_all_faces()

    def start(self):
        # to start the network we create a listen thread for incoming connections
        thread = threading.Thread(target=self.listen)
        thread.start()
        self.connectToNetwork()

    def close(self):
        self.sendAll(DISCONNECT_MESSAGE)  # Not sendToAllNetwork because we only need to disconnect from current conns
        self.run = False
        self.ledger.save()
