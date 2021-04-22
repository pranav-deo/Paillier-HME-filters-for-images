import sympy
import math

from math_utils import invmod, modpow, custom_frexp


def generate_keypair(num_digit):  # generate private and public keys
    p = sympy.randprime(10**(num_digit - 1), 10**(num_digit))
    q = sympy.randprime(10**(num_digit - 1), 10**(num_digit))
    while(p == q):
        q = sympy.randprime(10**(num_digit - 1), 10**(num_digit))
    n = p * q

    # private
    ll = (p - 1) * (q - 1)
    myu = invmod(ll, n)
    private = (ll, myu)

    # public
    public = (n, n + 1)
    return private, public


def encrypt(public, plain_):  # encrypt the plain data using public key 0<=plain<n
    plain, expo = custom_frexp(plain_)
    (n, g) = public
    r = sympy.randprime(0, n)
    while(math.gcd(r, n) != 1):
        r = sympy.randprime(0, n)
    n_sq = n**2
    r_n = modpow(r, n, n_sq)
    g_m = (1 + plain * n) % n_sq  # ((1+n)^m)(mod n^2)=(1+nm)(mod n^2)
    c = (r_n * g_m) % n_sq

    return c, expo


def decrypt(private, public, cipher):  # decrypt the cipher using public and private key
    (lam, myu) = private
    (n, g) = public
    n_sq = n**2
    # print("In decrypt: ", cipher)
    L_n = modpow(int(cipher[0]), int(lam), int(n_sq)) - 1
    L_n = L_n // n
    plain = (L_n * myu) % n
    plain = ((plain + math.floor(n / 2)) % n) - math.floor(n / 2)

    return plain * 2**cipher[1]


######################################################################################################################################
# ORIGINAL PAILLIER FUNCTIONS
######################################################################################################################################

def paillier_add(public, c1, c2):  # cipher of the addition of plain text
    (n, g) = public
    n_sq = n**2
    return (c1 * c2) % n_sq


def paillier_sub(public, c1, c2):  # cipher of the subtraction of plain text
    (n, g) = public
    n_sq = n**2
    return (c1 * invmod(c2, n_sq)) % n_sq


def paillier_mul(public, c1, m1):  # cipher of multiplication of 2 plain texts(1 private plain tect and 1 public plain text)
    (n, g) = public
    n_sq = n**2
    m1 = int(m1)
    c1 = int(c1)
    # print('=' * 100)
    # print(type(public))
    # print(type(c1), c1)
    # print(type(m1), m1)
    # print('=' * 100)
    return modpow(c1, m1, n_sq)

######################################################################################################################################
# PAILLIER FUNCTIONS MODIFIED FOR FLOATING POINT NUMBERS
######################################################################################################################################


def new_paillier_mul(public, c1, k):
    """ Returns c1 * k in cipher space where k is a constant FP number"""
    c2 = custom_frexp(k)
    m12 = paillier_mul(public, c1[0], c2[0])
    e12 = c1[1] + c2[1]
    return (m12, e12)


def new_paillier_add(public, c1, c2):
    """ Returns c1 + c2 in cipher space """
    if c1[1] <= c2[1]:
        temp = paillier_mul(public, c2[0], 2**(c2[1] - c1[1]))
        m3 = paillier_add(public, int(c1[0]), temp)
        return (m3, c1[1])
    else:
        temp = paillier_mul(public, c1[0], 2**(c1[1] - c2[1]))
        m3 = paillier_add(public, c2[0], temp)
        return (m3, c2[1])


def new_paillier_sub(public, c1, c2):
    """ Returns c1 - c2 in cipher space """
    if c1[1] <= c2[1]:
        temp = paillier_mul(public, c2[0], 2**(c2[1] - c1[1]))
        m3 = paillier_sub(public, c1[0], temp)
        return (m3, c1[1])
    else:
        temp = paillier_mul(public, c1[0], 2**(c1[1] - c2[1]))
        m3 = paillier_sub(public, c2[0], temp)
        return (m3, c2[1])
