import blockchain, threading, socket, pickle, time  # All part of Python standard libary (blockchain is my script)
socket.setdefaulttimeout(5)  # So socket.listen and socket.recv only run for 3 seconds to prevent program hanging

# These are commands we may receive from other nodes
DISCONNECT_MESSAGE = '!DISCONNECT'  # A connection is disconnected
STATUS_MESSAGE = '!STATUS'  # Just to check for a connection
SEND_CHAIN_MESSAGE = '!GIVECHAIN'  # We send this if we want the chain, if we receive this we send the chain

'''
This is the file ive spent the most time in. I HATE SOCKETS.
Ive spent AT LEAST 70 hours in this file and there are still 
soooo many bugs. Besides sockets sucking, Ive learned the most in 
this file
'''
class BlockchainNetwork:
    def __init__(self):
        self.run = True  # so the threads will stop
        self.HEADER = 10  # our socket header, meaning we can only handle messages size 2**HEADER
        self.PORT = 5050  # the port the servers will 'live' on
        self.MY_IP = socket.gethostbyname(socket.gethostname())
        self.MY_ADDR = (self.MY_IP, self.PORT)
        self.connections = []  # store all of our outgoing sockets
        self.clients = []  # store all of incoming sockets
        self.networkIps = []
        with open("data/network_Ips.txt", "r") as r: 
            for line in r.readlines(): self.networkIps.append(line.strip("\n"))
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a listening socket
        self.server.bind(self.MY_ADDR)
        self.ledger = blockchain.Blockchain()

    def send(self, conn, obj):
        print(f"[{conn.getsockname()}] sending {obj}...")
        time.sleep(1)  # to avoid clumping (it still rarely happens cuz of threading)
        dump = pickle.dumps(obj)  # serialize the obj
        msg = bytes(f'{len(dump):<{self.HEADER}}', 'utf-8') + dump  # pad the serialized obj
        try:
            conn.send(msg)  # send it off to the socket (not using .sendall cuz im a chad)
        except ConnectionError:  # if we are not connected anymore, catch this error
            self.close_connection(conn.sockbyname())

    def sendTo(self, ip, obj):
        for sock in self.connections:
            if sock[1][0] == ip:
                self.send(sock[0], obj)
                break

    def sendAll(self, obj): 
        for conn in self.connections: 
            self.send(conn[0], obj)
    
    def connectToNetwork(self):
        for ip in self.networkIps: 
            if ip != self.MY_IP:  # avoid connection loop
                self.connect(ip)
    
    def connect(self, ip):
        for conn in self.connections:
            if ip == conn[1][0]:  # having two outgoing sockets for the same server is silly
                print(f"[NET] already connected to {conn[0].getsockname()}")
                return
            if ip == self.MY_IP:
                print("[NET] not connecting to myself")
                return
        try:
            addr = (ip, self.PORT)
            print(f"[NET] connecting to {addr}...")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(addr)
            self.connections.append((s, addr))
            print(f"[NET] connected to {addr}")
        except socket.timeout: print(f"[NET] connection to {addr} timed out")
        except ConnectionRefusedError: print(f"[NET] connection to {addr} was refused")

    def close_connection(self, conn):
        print(f"trying to close {conn}, name: {conn.getsockname()}")
        for i, sock in enumerate(self.connections):
            if sock[0].getsockname()[0] == conn.getsockname()[0]:
                print(f"[NET] closing outgoing {self.connections[i]}")
                sock[0].close()
                self.connections.pop(i)
        for i, sock in enumerate(self.clients):
            if sock[0].getsockname()[0] == conn.getsockname()[0]:
                print(f"[NET] closing incoming {self.clients[i]}")
                sock[0].close()
                self.clients.pop(i)

    def handle_client(self, conn, addr):
        print(f"[NET] new incoming connection from {conn.getsockname()}")
        full_msg, new_msg = b'', True
        while self.run:
            try:
                msg = conn.recv(self.HEADER + 4069)  # receive the packet
                full_msg += msg
                if new_msg:  # find the new message length 
                    msg_length = int(msg[:self.HEADER])
                    new_msg = False
                
                if len(full_msg) - self.HEADER == msg_length:  # we know we received the full msg
                    received_msg = pickle.loads(full_msg[self.HEADER:])  # we are now safe to deserialize the received obj
                    full_msg, new_msg = b'', True  # any msg we receive now is a new msg
                    if received_msg == DISCONNECT_MESSAGE:
                        print(f'[{addr}] disconnected')
                        self.close_connection(conn)
                        break
                    elif received_msg == STATUS_MESSAGE: 
                        self.sendTo(addr[0], 'active')
                    elif received_msg == SEND_CHAIN_MESSAGE:
                        # we use a thread so we can continue to listen for receives in this socket
                        thread = threading.Thread(target=self.sendTo, args=(addr[0], self.ledger))
                        thread.start()
                    else: 
                        if type(received_msg) == blockchain.Identity: 
                            self.ledger.add_identity(received_msg)
                            if len(self.ledger.pending_identities) > 3:  # if we have more than 3 pending idens, we should mine a block
                                self.mineBlock()
                        elif type(received_msg) == blockchain.Block:
                            self.ledger.add_block(received_msg)
                        elif type(received_msg) == blockchain.Blockchain:
                            if received_msg.check_integrity() != True: 
                                return
                            if len(received_msg.chain) < len(self.ledger.chain): 
                                return
                            if received_msg.chain[0].cal_hash() != self.ledger.chain[0].cal_hash(): 
                                return
                            self.ledger.__dict__ = received_msg.__dict__
                            self.ledger.printChainInfo()
                    print(f"[{addr}] received {received_msg}")
            except socket.timeout: continue
            except ConnectionAbortedError:
                print(f"[{addr}] aborted")
                self.close_connection(conn)
                break
            except ConnectionResetError:
                self.close_connection(conn)
                break
    
    def listen(self):
        self.server.listen()
        print(f"[NET] listening on {self.server.getsockname()}...")
        while self.run:
            try: 
                conn, addr = self.server.accept()
                print(conn.getsockname(), addr)
            except socket.timeout: continue
            isvaild = True
            for sock in self.clients:
                if sock[1][0] == addr[0]:
                    conn.close()
                    isvaild = False
                    break
            if isvaild:
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.start()
                self.clients.append((conn, addr))
                self.connect(addr[0])
    
    def createIdentity(self, name, face_encoding):
        iden, qk, pk = self.ledger.create_identity(name, face_encoding)
        self.sendAll(iden)
        with open("data/keys.txt", "a+") as r:
            r.write(f"{name} {qk} {pk}\n")
        if len(self.ledger.pending_identities) > 4:
            thread = threading.Thread(target=self.mineBlock)
            thread.start()
        return qk, pk

    def mineBlock(self):
        block = self.ledger.mine_block()
        self.sendAll(block)

    def get_sockets(self):
        outgoings = []
        incomings = []
        for outgoing in self.connections:
            outgoings.append(outgoing[1])
        for incoming in self.clients:
            incomings.append(incoming[1])
        return outgoings, incomings

    def get_chain(self): return self.ledger
    def get_faces(self): return self.ledger.get_all_faces()
    def print_chain(self): self.ledger.print_chain()
    def print_chain_info(self): self.ledger.printChainInfo()

    def start(self):
        thread = threading.Thread(target=self.listen)  # start listening for connections
        thread.start()
        thread = threading.Thread(target=self.connectToNetwork)
        thread.start()

    def close(self):
        self.sendAll(DISCONNECT_MESSAGE)
        time.sleep(3)
        self.run = False
        self.ledger.save()
