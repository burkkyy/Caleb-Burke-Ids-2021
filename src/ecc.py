# this is the file that handles the eliptic curve cryptography
import random
import hashlib

'''
using ECC signatures because RSA IS SLOW AF
also ECC is way cooler than RSA
'''

INFINITY_POINT = None


class EllipticCurve:
    def __init__(self):
        """
        These values are predefined from:
        https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-186-draft.pdf
        """
        self.p = 26959946667150639794667015087019630673557916260026308143510066298881
        self.a = -3
        self.b = 18958286285566608000408668544493926415504680968679321075787234672564
        self.G = (
            19277929113566293071110308034699488026831934219452440156649784352033,
            19926808758034470970197974370888749184205991990603949537637343198772
        )
        self.n = 26959946667150639794667015087019625940457807714424391721682722368061

    def addition(self, point1, point2):
        """
        To 'add' to points on a elliptic curve, we find the linear line which goes through points 1 and 2, then we find
        the intersection point of that line onto the elliptic curve, then we reflect that point in the x-axis
        :param point1: some point on the curve
        :param point2: some point on the curve
        :return: resulting point of the elliptic addition
        """
        if point1 == INFINITY_POINT:
            return point2
        if point2 == INFINITY_POINT:
            return point1

        (x1, y1) = point1
        (x2, y2) = point2

        if self.equal_modp(x1, x2) and self.equal_modp(y1, -y2):
            return INFINITY_POINT

        if self.equal_modp(x1, x2) and self.equal_modp(y1, y2):
            u = self.reduce_modp((3 * x1 * x1 + self.a) * self.inverse_modp(2 * y1))
        else:
            u = self.reduce_modp((y1 - y2) * self.inverse_modp(x1 - x2))

        v = self.reduce_modp(y1 - u * x1)
        x3 = self.reduce_modp(u * u - x1 - x2)
        y3 = self.reduce_modp(-u * x3 - v)
        return x3, y3

    def multiple(self, k, P):
        """
        To multiply two points on a elliptic curve, we define the base point (some point on the graph, usually some
        predefined point called the generator point) and apply elliptic addition to itself k number of times.
        This is used primarily to generate the public key from the private key
        :param k: the factor by which to multiply
        :param P: the base point (generator point)
        :return: sudo random point
        """
        Q = INFINITY_POINT
        if k == 0:
            return Q
        while k != 0:
            if k & 1 != 0:
                Q = self.addition(Q, P)
            P = self.addition(P, P)
            k >>= 1
        return Q

    def is_point_on_curve(self, x, y):
        return self.equal_modp(y * y, x * x * x + self.a * x + self.b)

    def reduce_modp(self, x):
        return x % self.p

    def equal_modp(self, x, y):
        return self.reduce_modp(x - y) == 0

    def inverse_modp(self, x):
        if self.reduce_modp(x) == 0:
            return None
        return pow(x, self.p - 2, self.p)

    def inverse_mod(self, x, order):
        if self.reduce_modp(x) == 0:
            return None
        return pow(x, order - 2, order)

    def create_keys(self):
        """
        IN THE REAL WORLD THIS IS DANGEROUS TO USE AS THE RANDOM FUNCTION CAN BE REVERSED ENGINEERED, for this project
        this is fine as creating a PRNG from scratch would be too much work for what it is going to be used for
        :return: key pair
        """
        qk = random.randint(1, self.n - 1)
        pk = self.multiple(qk, self.G)
        # print(f"qk: {qk} \npk: {pk}\n")
        return qk, pk

    def sign(self, m, qk):
        """
        :param m: the message to be signed
        :param qk: the private key which will sign the message
        :return: elliptic signature
        """

        # Hash the message
        hashed_message = int(
            hashlib.sha1(m.encode()).hexdigest(),
            16
        )

        ''' 
        IN THE REAL WORLD THIS IS DANGEROUS TO USE AS THE RANDOM FUNCTION CAN BE REVERSED ENGINEERED, for this project
        this is fine as creating a PRNG from scratch would be too much work for what it is going to be used for.
        '''
        k = random.randint(1, self.n - 1)
        x1, y1 = self.multiple(k, self.G)

        r = x1 % self.n

        s = hashed_message + (r * qk)
        s = s * self.inverse_mod(k, self.n)
        s = s % self.n
        return r, s

    def verify(self, sig, m, pk):
        """
        :param sig: the elliptic curve signature
        :param m: the message which was signed
        :param pk: the public key of the signer
        :return: if the signature was derived from the private key
        """
        hashed_message = int(
            hashlib.sha1(m.encode()).hexdigest(),
            16
        )

        w = self.inverse_mod(sig[1], self.n)
        u1 = self.multiple(((hashed_message * w) % self.n), self.G)
        u2 = self.multiple(((sig[0] * w) % self.n), pk)

        checkpoint = self.addition(u1, u2)
        if checkpoint[0] == sig[0]:
            return True


if __name__ == "__main__":
    # mod = p
    # order = n
    P224 = EllipticCurve()
    qk1, pk1 = P224.create_keys()

    words = []
    for i in range(100):
        words.append(str(i))

    print("Starting 100 sign and verify check test...")
    import time
    old = time.time()
    for word in words:
        sig1 = P224.sign(word, qk1)
        # word = "10"
        check = P224.verify(sig1, word, pk1)
    print(time.time()-old)
