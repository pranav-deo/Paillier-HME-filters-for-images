import numpy as np

from crypt_utils import new_paillier_add, new_paillier_mul, new_paillier_sub, decrypt, encrypt


def merge_m_e(tup):
    """ Merges the mantissa and exponent channel to parse it in single greyscale image"""
    return tup[0] * 100000 + tup[1]


def unmerge_m_e(pixel):
    """ Unmerges the mantissa and exponent channel to perform operations on the ciphered image"""
    return (pixel // 100000, pixel % 100000)


def Im_encrypt(public, plain_im):
    cipher_im = np.asarray(plain_im)
    shape = cipher_im.shape
    cipher_im = cipher_im.flatten().tolist()
    cipher_im = [merge_m_e(encrypt(public, pixel)) for pixel in cipher_im]
    return np.asarray(cipher_im).reshape(shape)


def Im_decrypt(private, public, cipher_im):
    plain_im = np.asarray(cipher_im)
    shape = plain_im.shape
    plain_im = plain_im.flatten().tolist()
    plain_im = [decrypt(private, public, unmerge_m_e(pixel)) for pixel in plain_im]
    return np.clip(np.asarray(plain_im).reshape(shape), 0, 255)


def Brighten(public, cipher_im, factor):
    shape = cipher_im.shape
    bright_img = cipher_im.flatten().tolist()
    bright_img = [merge_m_e(new_paillier_add(public, unmerge_m_e(pixel), encrypt(public, factor))) for pixel in bright_img]
    return np.asarray(bright_img).reshape(shape)


def Negation(public, cipher_im):
    shape = cipher_im.shape
    negated_img = cipher_im.flatten().tolist()
    negated_img = [merge_m_e(new_paillier_sub(public, encrypt(public, 255), unmerge_m_e(pixel))) for pixel in negated_img]
    return np.asarray(negated_img).reshape(shape)


def LPF(public, cipher_im):
    shape = cipher_im.shape
    lpf_img = cipher_im.flatten().tolist()
    lpf_img = [paillier_sub(public, encrypt(public, 255), pixel) for pixel in lpf_img]
    return np.asarray(lpf_img).reshape(shape)
