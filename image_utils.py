import numpy as np

from crypt_utils import new_paillier_add, new_paillier_mul, new_paillier_sub, decrypt, encrypt
from math_utils import gkern


def merge_m_e(tup):
    """
    Merges the mantissa and exponent channel to parse it in single greyscale image

        Give one sign byte and 2 bytes for exponent
    """
    if abs(tup[1]) > 99:
        assert 564 == 5464
    if tup[1] >= 0:
        return tup[0] * 1000 + tup[1]
    else:
        return tup[0] * 1000 + 100 + abs(tup[1])


def unmerge_m_e(pixel):
    """ Unmerges the mantissa and exponent channel to perform operations on the ciphered image"""
    val = (pixel // 1000, pixel % 1000)
    if val[1] > 100:
        return (val[0], -1 * (val[1] % 100))
    else:
        return val


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
    negated_img = [merge_m_e(new_paillier_add(public, encrypt(public, 255), new_paillier_mul(public, unmerge_m_e(pixel), -1))) for pixel in negated_img]
    return np.asarray(negated_img).reshape(shape)


def LPF(public, cipher_im, filter_type='linear', kernal_size=3):
    row, column = cipher_im.shape
    lpf_img = np.zeros(cipher_im.shape).astype(int)
    for rr in range(row):
        for cc in range(column):
            lpf_img[rr][cc] = merge_m_e(encrypt(public, 0))

    if filter_type == 'gaussian':
        kernal = np.around(gkern(kernal_size, nsig=3), decimals=3)
    else:
        kernal = np.around(np.ones((kernal_size, kernal_size)) / (kernal_size * kernal_size), decimals=3)

    # print("kernal", kernal)
    for rr in range(row):
        for cc in range(column):
            for ii in np.linspace(-kernal_size // 2 + 1, kernal_size // 2, kernal_size).astype(int).tolist():
                if rr + ii < 0 or ii + rr >= row:
                    continue
                for jj in np.linspace(-kernal_size // 2 + 1, kernal_size // 2, kernal_size).astype(int).tolist():
                    if cc + jj < 0 or jj + cc >= column:
                        continue
                    # temp = lpf_img[rr][cc]
                    lpf_img[rr][cc] = merge_m_e(new_paillier_add(public, unmerge_m_e(lpf_img[rr][cc]), new_paillier_mul(public, unmerge_m_e(cipher_im[rr + ii][cc + jj]), kernal[kernal_size // 2 + ii][kernal_size // 2 + jj])))
                    # if decrypt(private, public, unmerge_m_e(lpf_img[rr][cc])) < 0:
                    #     tmp = decrypt(private, public, new_paillier_mul(public, unmerge_m_e(cipher_im[rr + ii][cc + jj]), 1 / 9))
                    # print("prev pixel", decrypt(private, public, unmerge_m_e(temp)))
                    # print("current multi", tmp)
                    # print("Addition", decrypt(private, public, unmerge_m_e(lpf_img[rr][cc])))
                    # assert 1 == 0
    return lpf_img


def Sharpen(public, cipher_im, k):
    row, column = cipher_im.shape
    shrp_img = np.zeros(cipher_im.shape).astype(int)
    for rr in range(row):
        for cc in range(column):
            shrp_img[rr][cc] = merge_m_e(encrypt(public, 0))

    lpf_img = LPF(public, cipher_im, 'gaussian', 3)

    for rr in range(row):
        for cc in range(column):
            t1 = new_paillier_mul(public, unmerge_m_e(cipher_im[rr][cc]), k + 1)
            t2 = new_paillier_mul(public, unmerge_m_e(lpf_img[rr][cc]), k)
            shrp_img[rr][cc] = merge_m_e(new_paillier_sub(public, t2, t1))
    return shrp_img


# def Dilation(public, cipher_im):
#     """ Assuming input image is binary i.e. it has only 0 and 255 """
#     row, column = cipher_im.shape
#     shrp_img = np.zeros(cipher_im.shape).astype(int)
#     for rr in range(row):
#         for cc in range(column):
#             shrp_img[rr][cc] = merge_m_e(encrypt(public, 0))

#     for rr in range(row):
#         for cc in range(column):
#             shrp_img[rr][cc] = merge_m_e(new_paillier_add(public, unmerge_m_e(cipher_im[rr][cc]), unmerge_m_e(shrp_img[rr][cc])))
#             for ii in [-1, 0, 1]:
#                 if rr + ii < 0 or ii + rr >= row:
#                     continue
#                 for jj in [-1, 0, 1]:
#                     if cc + jj < 0 or jj + cc >= column:
#                         continue
#                         if ii == 0 and jj == 0:
#                             continue
#                     fraction_sub = new_paillier_mul(public, unmerge_m_e(cipher_im[rr + ii][cc + jj]), 1 / 9)
#                     shrp_img[rr][cc] = merge_m_e(new_paillier_sub(public, unmerge_m_e(shrp_img[rr][cc]), fraction_sub))
#     return shrp_img

def Edge(public, cipher_im):
    row, column = cipher_im.shape
    Gx = np.zeros(cipher_im.shape).astype(int)
    Gy = np.zeros(cipher_im.shape).astype(int)

    kernal_size = 3
    kernal_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    kernal_y = kernal_x.T

    for rr in range(row):
        for cc in range(column):
            Gx[rr][cc] = merge_m_e(encrypt(public, 0))
            Gy[rr][cc] = merge_m_e(encrypt(public, 0))

    for rr in range(row):
        for cc in range(column):
            for ii in np.linspace(-kernal_size // 2 + 1, kernal_size // 2, kernal_size).astype(int).tolist():
                if rr + ii < 0 or ii + rr >= row:
                    continue
                for jj in np.linspace(-kernal_size // 2 + 1, kernal_size // 2, kernal_size).astype(int).tolist():
                    if cc + jj < 0 or jj + cc >= column:
                        continue
                    Gx[rr][cc] = merge_m_e(new_paillier_add(public, unmerge_m_e(Gx[rr][cc]), new_paillier_mul(public, unmerge_m_e(cipher_im[rr + ii][cc + jj]), kernal_x[kernal_size // 2 + ii][kernal_size // 2 + jj])))
                    Gy[rr][cc] = merge_m_e(new_paillier_add(public, unmerge_m_e(Gy[rr][cc]), new_paillier_mul(public, unmerge_m_e(cipher_im[rr + ii][cc + jj]), kernal_y[kernal_size // 2 + ii][kernal_size // 2 + jj])))
    return Gx, Gy
