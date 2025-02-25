import os
import random

from PIL import Image
import numpy as np

# horizontal gradient
gradient_horizontal = np.array([
    [[(255 / 64) * i, 255, 255] for i in range(64)] for _ in range(64)
], dtype=np.uint8)

image = Image.fromarray(gradient_horizontal, mode="HSV")

if not os.path.exists('.testing/png_in/gradients/horizontal.png'):
    open('.testing/png_in/gradients/horizontal.png', 'x').close()

image.convert("RGB").save('.testing/png_in/gradients/horizontal.png')

# vertical gradient
gradient_vertical = np.array([
    [[(255 / 64) * i, 255, 255] for _ in range(64)] for i in range(64)
], dtype=np.uint8)

image = Image.fromarray(gradient_vertical, mode="HSV")

if not os.path.exists('.testing/png_in/gradients/vertical.png'):
    open('.testing/png_in/gradients/vertical.png', 'x').close()

image.convert("RGB").save('.testing/png_in/gradients/vertical.png')

# diagonal gradient
gradient_diagonal = np.array([
    [[(255 / (64 + 63)) * (i + j), 255, 255] for i in range(64)] for j in range(64)
], dtype=np.uint8)

image = Image.fromarray(gradient_diagonal, mode="HSV")

if not os.path.exists('.testing/png_in/gradients/diagonal.png'):
    open('.testing/png_in/gradients/diagonal.png', 'x').close()

image.convert("RGB").save('.testing/png_in/gradients/diagonal.png')

# random spread
gradient_random = np.array([
    [[random.randint(0, 255), 255, 255] for _ in range(64)] for _ in range(64)
], dtype=np.uint8)

image = Image.fromarray(gradient_random, mode="HSV")

if not os.path.exists('.testing/png_in/gradients/random.png'):
    open('.testing/png_in/gradients/random.png', 'x').close()

image.convert("RGB").save('.testing/png_in/gradients/random.png')