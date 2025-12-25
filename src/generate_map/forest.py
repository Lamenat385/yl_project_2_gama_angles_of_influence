import numpy as np
import opensimplex as op


def get_forest_mask(N):
    width, height = N, N
    scale = 100
    x = np.linspace(0, width / scale, width)
    y = np.linspace(0, height / scale, height)
    noise_fast = op.noise2array(x, y)
    noise_mask = np.where(noise_fast <= 0, 0, noise_fast)
    noise_mask = np.where(noise_fast > 0, 1, noise_mask)
    return noise_mask