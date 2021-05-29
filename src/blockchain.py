from datetime import datetime
import hashlib, pickle, json, os, time
import ecc as ecc

P224 = ecc.EllipticCurve()


class Identity:
    def __init__(self, pk, name, face_encoding):
        """
        :param pk: public key of Identity
        :param name: Name of owner of Identity
        :param face_encoding: The face encoding of Identity
        """
        self.owner_pub_key = pk
        self.name = name
        self.encoding = face_encoding.tolist()
        self.signature = None
    
    def cal_hash(self):
        identity_txt = str(self.owner_pub_key) + self.name + str(self.encoding)
        return hashlib.sha256(identity_txt.encode()).hexdigest()

    def sign(self, private_key):
        # We use the ecc signature func to sign and verify signatures
        self.signature = P224.sign(
            self.cal_hash(),
            private_key,
        )

    def is_valid(self):
        if self.signature:
            return P224.verify(
                self.signature, self.cal_hash(), self.owner_pub_key
            )
        return False

    def to_string(self):
        # I copied this off stackoverflow
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class Block:
    def __init__(self, identities, prevHash):
        """
        :param identities: list of Identities to be put into this block
        :param prevHash: the prev block hash
        """
        self.timeStamp = str(datetime.now())
        self.identities = identities
        self.nonce = 0
        self.prevHash = prevHash
        self.hash = self.cal_hash()

    def cal_hash(self):
        block_txt = self.timeStamp + str([i.to_string() for i in self.identities]) + str(self.nonce) + self.prevHash
        return hashlib.sha256(block_txt.encode()).hexdigest()

    def mine(self, difficulty):
        """
        We 'mine' a block by calculating its hash, checking if it starts with n number of 0's, then if not increase
        the nonce of the block by 1 and repeat

        :param difficulty: the 'n' number of 0's
        :return: None
        """
        while self.hash[:difficulty] != "0"*difficulty:
            self.nonce += 1
            self.hash = self.cal_hash()
        print(self.hash, self.nonce)

    def has_valid_identities(self):
        for identity in self.identities:
            if not identity.is_valid():
                return False
        return True

    def to_string(self):
        # I copied this off stackoverflow
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class Blockchain:
    def __init__(self):
        self.path = "data/ledger.pkl"
        if not self.load():
            self.chain = [self.create_genesis_block()]
            self.pending_identities = []
            self.difficulty = 4
            
    def create_genesis_block(self):
        return Block("", "")

    def check_integrity(self):
        for block in range(1, len(self.chain)):
            if self.chain[block].hash != self.chain[block].cal_hash():
                return False
            if self.chain[block].prevHash != self.chain[block - 1].hash:
                return False
            if not self.chain[block].has_valid_identities():
                return False
        return True

    def mine_block(self):
        start = time.time()
        print(f"[BLOCKCHAIN] mining block at {self.difficulty} difficulty...")
        block = Block(self.pending_identities, self.chain[-1].hash)
        block.mine(self.difficulty)
        print(f"[BLOCKCHAIN] mined block {block.hash} in {time.time() - start}")
        self.chain.append(block)
        self.pending_identities = []
        return block

    def create_identity(self, name, face_encoding):
        qk, pk = P224.create_keys()
        identity = Identity(pk, name, face_encoding)
        identity.sign(qk)
        if identity.is_valid():
            self.pending_identities.append(identity)
            return identity, qk, pk
        return

    def add_identity(self, identity):
        if type(identity) != Identity:
            return False
        if not identity.is_valid():
            return False
        self.pending_identities.append(identity)

    def add_block(self, block):
        if type(block) != Block:
            print("FAILED #1")
            return False
        if block.hash != block.cal_hash():
            print("FAILED #2")
            return False
        if block.hash[:self.difficulty] != "0"*self.difficulty:
            print("FAILED #3")
            return False
        if block.prevHash != self.chain[-1].hash:
            print("FAILED #4")
            return False
        if not block.has_valid_identities():
            print("FAILED #5")
            return False
        for identity in block.identities:
            for i, iden in enumerate(self.pending_identities):
                if identity.cal_hash == iden.cal_hash:
                    self.pending_identities.pop(i)
        self.chain.append(block)
        return True

    def get_block(self, index):
        return self.chain[index]

    def get_face(self, name):
        for block in self.chain[1:]:
            for identity in block.identities:
                if identity.name == name:
                    return identity.encoding

    def get_all_faces(self):
        faces = []
        names = []
        for block in self.chain[1:]:
            for identity in block.identities:
                faces.append(identity.encoding)
                names.append(identity.name)
        return names, faces

    def print_chain(self):
        for block in self.chain:
            print(block.to_string())

    def printChainInfo(self):
        totalBlocks = len(self.chain)
        totalIdentities = 0
        for block in self.chain:
            totalIdentities += len(block.identities)
        print(f"[BLOCKCHAIN] total blocks: {totalBlocks}, total identities: {totalIdentities}")
    
    def save(self):
        try:
            os.remove(self.path)
        except OSError:
            print(f"[FILE IO] creating file at {self.path}...")
        with open(self.path, "wb") as r:
            pickle.dump(self.__dict__, r)

    def load(self):
        try:
            with open(self.path, "rb") as r:
                self.__dict__ = pickle.load(r)
            return True
        except Exception as err:
            print(f"[FILE IO] {err}")
            return False
