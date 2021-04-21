import libnum
import math


def invmod(a, p):  # a*b=1(mod p) return b
    return libnum.invmod(a, p)


def modpow(b, e, m):  # return b^e(mod m)
    result = pow(b, e, m)
    return result


def custom_frexp(num):
    man, exp = math.frexp(num)

    while (not math.isclose(man, int(man), rel_tol=1e-9)) or exp > 0:
        man *= 2
        exp -= 1

    return int(man), exp
