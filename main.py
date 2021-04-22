import sys
import numpy as np
np.set_printoptions(threshold=sys.maxsize)

from PIL import Image
import matplotlib.pyplot as plt
import time

from crypt_utils import generate_keypair
from image_utils import Im_encrypt, Im_decrypt, Brighten, Negation, LPF, Sharpen, Edge, Dilation, Hist_equal

MAX_IMG_DIM = 400

private_key, public_key = generate_keypair(num_digit=4)

f, ax = plt.subplots(3, 3)

img = Image.open('lena.jpg').convert('L')

img = np.asarray(img.resize((MAX_IMG_DIM, img.height * MAX_IMG_DIM // img.width)))

s = time.time()

############################################################################################################
# ORIGINAL IMAGE
############################################################################################################

ax[0][0].imshow(img, cmap='gray', vmin=0, vmax=255)
ax[0][0].set_title('Orignal image')

############################################################################################################
# ENCRYPTED IMAGE
############################################################################################################

cipher_image = Im_encrypt(public_key, img)
ax[0][1].imshow(cipher_image.astype(float))
ax[0][1].set_title('Encrypted image')


############################################################################################################
# DECRYPTED IMAGE
############################################################################################################

r_img = Im_decrypt(private_key, public_key, cipher_image)
ax[0][2].imshow(r_img, cmap='gray', vmin=0, vmax=255)
ax[0][2].set_title('Decrypted image')


############################################################################################################
# SHARPENED IMAGE
############################################################################################################

s_img = Im_decrypt(private_key, public_key, Sharpen(public_key, cipher_image, 1))
ax[1][0].imshow(s_img, cmap='gray', vmin=0, vmax=255)
ax[1][0].set_title('Sharpened image')

############################################################################################################
# LOW PASS FILTERED IMAGE
############################################################################################################

l_img = Im_decrypt(private_key, public_key, LPF(public_key, cipher_image, filter_type='linear', kernal_size=3))
ax[1][1].imshow(l_img, cmap='gray', vmin=0, vmax=255)
ax[1][1].set_title('LPF image')

############################################################################################################
# BRIGHTENED IMAGE
############################################################################################################

b_img = Im_decrypt(private_key, public_key, Brighten(public_key, cipher_image, 100))
ax[1][2].imshow(b_img, cmap='gray', vmin=0, vmax=255)
ax[1][2].set_title('Brightened image')

############################################################################################################
# NEGATED IMAGE
############################################################################################################

n_img = Im_decrypt(private_key, public_key, Negation(public_key, cipher_image))
ax[2][0].imshow(n_img, cmap='gray', vmin=0, vmax=255)
ax[2][0].set_title('Negative image')

############################################################################################################
# EDGES OF IMAGE
############################################################################################################

Gx = Im_decrypt(private_key, public_key, Edge(public_key, cipher_image)[0])
Gy = Im_decrypt(private_key, public_key, Edge(public_key, cipher_image)[1])
G = np.sqrt(Gx**2 + Gy**2)
ax[2][1].imshow(G, cmap='gray', vmin=0, vmax=255)
ax[2][1].set_title('Edge image')


############################################################################################################
# HISTOGRAM EQUALIZED IMAGE
############################################################################################################

im_new = np.copy(img)
histogram_array = np.bincount(img.flatten(), minlength=256)
hist_cipher = Im_encrypt(public_key, histogram_array)
pixel_transform = Im_decrypt(private_key, public_key, Hist_equal(public_key, hist_cipher, im_new.shape, private_key))

row, column = im_new.shape
for rr in range(row):
    for cc in range(column):
        im_new[rr][cc] = pixel_transform[im_new[rr][cc]]

ax[2][2].imshow(im_new, cmap='gray')
ax[2][2].set_title('Histogram equalized image')


plt.show()

############################################################################################################
# DILATED IMAGE
############################################################################################################

f, ax = plt.subplots(1, 2)

bin_img = Image.open('dil.jpg').convert('L')
bin_img = np.asarray(bin_img.resize((MAX_IMG_DIM, bin_img.height * MAX_IMG_DIM // bin_img.width)))
bin_cipher_image = Im_encrypt(public_key, bin_img)


d_img = Im_decrypt(private_key, public_key, Dilation(public_key, bin_cipher_image, kernal_size=3))
d_img = np.clip(d_img, 0, 1)

ax[0].imshow(bin_img, cmap='gray')
ax[0].set_title('Binary input')

ax[1].imshow(d_img, cmap='gray')
ax[1].set_title('Dilated output')


print("Time taken: %ds" % (time.time() - s))
plt.show()
