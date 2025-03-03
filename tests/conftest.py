import numpy as np
import PIL.Image


def images_equal(a: PIL.Image.Image, b: PIL.Image.Image) -> bool:
    return np.array_equal(np.asarray(a), np.asarray(b))
