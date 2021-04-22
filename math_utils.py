import libnum
import math
import scipy.stats as st
import numpy as np


def invmod(a, p):  # a*b=1(mod p) return b
    return libnum.invmod(a, p)


def modpow(b, e, m):  # return b^e(mod m)
    result = pow(b, e, m)
    return result


def custom_frexp(num):
    man, exp = math.frexp(num)

    while (not math.isclose(man, int(man), rel_tol=1e-4)) or exp > 0:
        man *= 2
        exp -= 1

    return int(man), exp


def gkern(kernlen=21, nsig=3):
    """Returns a 2D Gaussian kernel."""
    x = np.linspace(-nsig, nsig, kernlen + 1)
    kern1d = np.diff(st.norm.cdf(x))
    kern2d = np.outer(kern1d, kern1d)
    return kern2d / kern2d.sum()
