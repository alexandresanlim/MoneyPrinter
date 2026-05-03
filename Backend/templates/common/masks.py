import numpy as np

def circle_mask(size):
    mask = 255 * np.ones((size, size, 3), dtype=np.uint8)
    center = size // 2
    Y, X = np.ogrid[:size, :size]
    mask_area = (X - center) ** 2 + (Y - center) ** 2 <= center ** 2
    mask[~mask_area] = 0
    return mask

def radius_mask(size, radius):
    mask = 255 * np.ones((size, size, 3), dtype=np.uint8)
    Y, X = np.ogrid[:size, :size]
    mask_area = (X <= radius) | (X >= size - radius) | (Y <= radius) | (Y >= size - radius) | ((X - size + radius)**2 + (Y - radius)**2 <= radius**2) | ((X - radius)**2 + (Y - size + radius)**2 <= radius**2)
    mask[~mask_area] = 0
    return mask