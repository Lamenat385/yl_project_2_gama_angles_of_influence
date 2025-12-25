import opensimplex as op
import numpy as np
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
from random import seed
from rivers import add_rivers
from stones import add_stones
from fossils import get_fossils_mask
from forest import get_forest_mask

def set_seed(s):
    seed(s)
    np.random.seed(s)
    op.seed(s)

def get_small_land(N):
    width, height = N, N
    scale = 10
    x = np.linspace(0, width / scale, width)
    y = np.linspace(0, height / scale, height)
    noise_fast = op.noise2array(x, y)
    return (noise_fast + 1) / 2


def get_big_land_mask(N):
    width, height = N, N
    scale = 300
    x = np.linspace(0, width / scale, width)
    y = np.linspace(0, height / scale, height)
    noise_fast = op.noise2array(x, y)
    noise_mask = np.where(noise_fast < 0, 1, noise_fast)
    return np.where(noise_fast > 0, 0, noise_mask)


def generation_world_map(N, M, lenght, rt, m, rad,s,M1,lenght1,rt1,m1,rad1):
    set_seed(s)
    mapp = get_small_land(N)
    mapp = np.array(gaussian_filter(mapp, sigma=10))
    mapp = add_stones(mapp,M1,lenght1,rt1,m1, rad1)
    mapp = np.array(gaussian_filter(mapp, sigma=5))
    mapp = add_rivers(mapp, M, lenght, rt, m, rad)
    land_mask = get_big_land_mask(N)
    mapp = np.where(land_mask == 0, 0, mapp)
    mapp = np.array(gaussian_filter(mapp, sigma=1))
    fossils = get_fossils_mask(N)
    fossils = np.where(land_mask == 0, 0, fossils)
    forest_mask=get_forest_mask(N)
    forest_mask = np.where(land_mask == 0, 0, forest_mask)
    forest_mask = np.where(mapp > 0.6, 0, forest_mask)
    forest_mask = np.where(mapp < 0.2, 0, forest_mask)
    return mapp,fossils,forest_mask
#(512, 3, 20, 0.09, 30, 2,67,3,10,0.2,50,7.5)
