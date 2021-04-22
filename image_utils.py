import numpy as np

from crypt_utils import new_paillier_add, new_paillier_mul, new_paillier_sub, decrypt, encrypt


def merge_m_e(tup):
    """ Merges the mantissa and exponent channel to parse it in single greyscale image"""
    return tup[0] * 1000 + tup[1]


def unmerge_m_e(pixel):
    """ Unmerges the mantissa and exponent channel to perform operations on the ciphered image"""
    return (pixel // 1000, pixel % 1000)


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


def LPF(public, cipher_im, private):
    # shape = cipher_im.shape
    # lpf_img = cipher_im.flatten().tolist()
    # lpf_img = [paillier_sub(public, encrypt(public, 255), pixel) for pixel in lpf_img]
    # return np.asarray(lpf_img).reshape(shape)
    row, column = cipher_im.shape
    lpf_img = np.zeros(cipher_im.shape).astype(int)
    for rr in range(row):
        for cc in range(column):
            lpf_img[rr][cc] = merge_m_e(encrypt(public, 0))

    for rr in range(row):
        for cc in range(column):
            for ii in [-1, 0, 1]:
                if rr + ii < 0 or ii + rr >= row:
                    continue
                for jj in [-1, 0, 1]:
                    if cc + jj < 0 or jj + cc >= column:
                        continue
                    # print(rr, cc, ii, jj)
                    lpf_img[rr][cc] = merge_m_e(new_paillier_add(public, unmerge_m_e(lpf_img[rr][cc]), unmerge_m_e(cipher_im[rr + ii][cc + jj])))
            print("B", rr, cc, decrypt(private, public, unmerge_m_e(lpf_img[rr][cc])))
            print("B1", rr, cc, unmerge_m_e(lpf_img[rr][cc]))
            lpf_img[rr][cc] = merge_m_e(new_paillier_mul(public, unmerge_m_e(lpf_img[rr][cc]), 1 / 8))
            print("A", rr, cc, decrypt(private, public, unmerge_m_e(lpf_img[rr][cc])))
    return lpf_img
