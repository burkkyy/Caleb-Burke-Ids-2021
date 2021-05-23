import blockchain
import threading, socket, pickle, time  # All part of Python standard libary

socket.setdefaulttimeout(3)  # So socket.listen and socket.recv only run for 3 seconds to prevent program hanging

with open("data/network_Ips.txt", "r") as r:
    NETWORK_IPS = []
    for line in r.readlines():
        NETWORK_IPS.append(line.strip("\n"))
print(f"NETWORK IPS KNOWN: {NETWORK_IPS}")

# These are commands we may receive
DISCONNECT_MESSAGE = '!DISCONNECT'  # A connection is disconnected
STATUS_MESSAGE = '!STATUS'  # Just to check for a connection
SEND_CHAIN_MESSAGE = '!GIVECHAIN'  # We send this if we want the chain, if we receive this we send the chain
RECEIVE_CHAIN_MESSAGE = '!CHAIN'  # We have received a copy of the chain or we are going to send the chain
NEW_IDENTITY_MESSAGE = '!NEWIDENTITY'  # We are receving a new Identity from sender
NEW_BLOCK_MESSAGE = '!NEWBLOCK'  # We are receving a new 'mined' block from the sender

class BlockchainNetwork:
    def __init__(self):
        # Networking stuff
        self.HEADER = 4069  # Expected file receive size, 4 kilobytes
        self.PORT = 5050  # The port in which we will be 'listening and talking' through
        self.IP = socket.gethostbyname(socket.gethostname())  # find my local ip
        self.ADDR_SERVER = (self.IP, self.PORT)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket obj for allowing connections
        self.server.bind(self.ADDR_SERVER)  # 'Bind' it on this machine on port 5050
        self.clients = []  # Store all current and imcoming connections
        self.run = True  # If the network should be active
        
        # Blockchain Stuff
        self.ledger = blockchain.Blockchain()
        self.ledger.printChainInfo()

        '''
        Socket receive / send structure:
        SENDING STRUCTURE: (ip, protocol, payload)
        RECEIVING STRUCTURE: (ip, protocol, payload) 
        '''

    def send(self, conn, obj=None, protocol="!"):
        """
        conn: Ptr of the socket obj we wish to send to
        obj: Object we wish to send
        protocol: The 'send type', ex !NEWBLOCK
        """
        dump = pickle.dumps((protocol, obj))
        conn.sendall(dump)

    def sendToAll(self, obj=None, protocol="!"):
        """
        obj: the object we wish to send
        protocol: the 'send type', ex !NEWBLOCK
        """
        dump = pickle.dumps((protocol, obj))
        for client in self.clients:
            client[0].sendall(dump)

    def sendToAllNetwork(self, obj, protocol="!"):
        for ip in NETWORK_IPS:
            self.connect(ip, protocol, obj)

    def handleReceive(self, message, conn):
        # THIS CODE IS EXTREMLY INSECURE BUT I AM NOT FOCUSING ON THIS PART OF THE PROJECT
        if message[0] == "!":
            pass
        elif message[0] == DISCONNECT_MESSAGE:
            print(f"[NETWORK] received vaild protocol: {message[0]}")
            conn.close()
        elif message[0] == STATUS_MESSAGE:
            print(f"[NETWORK] received vaild protocol: {message[0]}")
            self.send(conn, True)
        elif message[0] == SEND_CHAIN_MESSAGE:
            print(f"[NETWORK] received vaild protocol: {message[0]}")
            self.send(conn, self.ledger)
        elif message[0] == RECEIVE_CHAIN_MESSAGE:
            print(f"[NETWORK] received vaild protocol: {message[0]}")
            b = message[1]
            if type(b) == blockchain.Blockchain and b.check_integrity:
                self.ledger = b
        elif message[0] == NEW_IDENTITY_MESSAGE:
            print(f"[NETWORK] received vaild protocol: {message[0]}")
            self.ledger.add_identity(message[1])
        elif message[0] == NEW_BLOCK_MESSAGE:
            print(f"[NETWORK] received vaild protocol: {message[0]}")
            self.ledger.add_block(message[1])
        print(f"[NETWORK] received invaild protocol: {message[0]}")

    def handleClient(self, conn, addr, index):
        print(f"\n[NET] new connection from {addr}")
        """
        conn: Ptr to the socket object we wish to handle
        addr: Address of the socket object, why cant we just do socket.raddr??
        index: Index of conn in self.clients
        """
        while self.run:
            '''
            Below we try to accept received data for 5 seconds, 
            then we raise socket.timeout so conn.recv() doesnt 
            run forever, 5 secs because socket.setdefaulttimeout(5)
            '''
            try:
                receive = conn.recv(self.HEADER)
            except socket.timeout:
                continue
            except ConnectionResetError as err:
                print(f"[{addr}] {err}")
                break

            if receive:
                receive = pickle.loads(receive)
                self.handleReceive(receive, conn)

    def listen(self):
        print(f"[NET] server listening on {self.ADDR_SERVER}")
        self.server.listen()
        while self.run:
            # Below we try to accept conns for 5 seconds, then we raise
            # socket.timeout so server.accept() doesnt run forever
            try:
                conn, addr = self.server.accept()
            except socket.timeout:
                continue

            # At this point, a conn was established so we create a new 
            # thread in order to handle this conn
            thread = threading.Thread(
                target=self.handleClient,
                args=(conn, addr, len(self.clients))
            )
            thread.start()

            # then append a ptr of the socket to clients
            self.clients.append([conn, addr])

    def connect(self, ip, protocol="!", obj=None):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                print((ip, self.PORT))
                s.connect((ip, self.PORT))  # Connect to desired server
                dump = pickle.dumps((protocol, obj))  # Create byte obj of what we want to send
                s.sendall(dump)  # Send the byte obj
                receive = s.recv(self.HEADER)  # Wait for a response
                if receive:
                    receive = pickle.loads(receive)  # Decode the response
                    self.handleReceive(receive, s)  # Handle the response
                    s.sendall(DISCONNECT_MESSAGE.encode('utf-8'))  # We are done with this connection, we now send server disconnect message encoded in utf-8
                s.close()  # Close connection between server
        except socket.timeout:
            return
        except ConnectionRefusedError:
            return

    def createIdentity(self, name, face_encoding):
        iden, qk, pk = self.ledger.create_identity(name, face_encoding)
        self.sendToAllNetwork(iden, NEW_IDENTITY_MESSAGE)
        with open("data/keys.txt", "a+") as r:
            r.write(f"\n{name} {qk} {pk}")
        return qk, pk

    def mineBlock(self):
        block = self.ledger.mine_block()
        self.sendToAllNetwork(block, NEW_BLOCK_MESSAGE)

    def get_conns(self):
        return self.clients

    def get_faces(self):
        return self.ledger.get_all_faces()

    def start(self):
        # to start the network we create a listen thread for incoming connections
        thread = threading.Thread(target=self.listen)
        thread.start()

    def close(self):
        self.sendToAll(protocol=DISCONNECT_MESSAGE)  # Not sendToAllNetwork because we only need to disconnect from current conns
        self.run = False
        self.ledger.save()
