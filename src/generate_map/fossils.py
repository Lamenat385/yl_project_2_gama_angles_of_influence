import numpy as np
import opensimplex as op


def get_fossils_mask(N):
    width, height = N, N

    # чёрный метал
    scale = 75
    x = np.linspace(0, width / scale, width)
    y = np.linspace(0, height / scale, height)
    noise_s = op.noise2array(x, y)

    scale = 5
    x = np.linspace(0, width / scale, width)
    y = np.linspace(0, height / scale, height)
    noise_fast = op.noise2array(x, y)

    noise_mask = np.where(noise_fast <= 0.5, 0, noise_fast)
    noise_mask = np.where(noise_fast > 0.5, 1, noise_mask)
    noise_mask = np.where(noise_s <= 0, 0, noise_mask)

    # топливо
    scale = 30
    x = np.linspace(0, width / scale, width)
    y = np.linspace(0, height / scale, height)
    noise_fast = op.noise2array(x, y)
    noise_mask = np.where(noise_fast > 0.6, 3, noise_mask)

    # цветной метал
    scale = 20
    x = np.linspace(0, width / scale, width)
    y = np.linspace(0, height / scale, height)
    noise_fast = op.noise2array(x, y)
    noise_mask = np.where(noise_fast > 0.7, 2, noise_mask)

    # уран
    scale = 50
    x = np.linspace(0, width / scale, width)
    y = np.linspace(0, height / scale, height)
    noise_fast = op.noise2array(x, y)
    noise_mask = np.where(noise_fast > 0.7, 4, noise_mask)

    return noise_mask
