import opensimplex as op
import numpy as np
from matplotlib import pyplot as plt
from scipy.ndimage import gaussian_filter
from random import seed
from src.generate_map.rivers import add_rivers
from src.generate_map.stones import add_stones
from src.generate_map.fossils import get_fossils_mask
from src.generate_map.forest import get_forest_mask
from PIL import Image


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
    noise_mask = np.where(noise_fast > 0, 0, noise_mask)

    scale = 50
    x = np.linspace(0, width / scale, width)
    y = np.linspace(0, height / scale, height)
    noise_fast = op.noise2array(x, y)
    noise_mask = np.where(noise_fast < -0.5, 1, noise_mask)
    return noise_mask


def height_to_color(H):
    H = max(0.0, min(1.0, H))
    if H < 0.3:
        # Градиент от темно-синего (0, 0, 0.4) до светло-голубого (0.5, 0.8, 1.0)
        t = H / 0.3  # Нормализуем в [0, 1) для интерполяции
        # Темно-синий -> светло-голубой
        R = 0.2 * t  # от 0 до 0.5
        G = 0.2 * t  # от 0 до 0.8
        B = 0.4 + 0.6 * t  # от 0.4 до 1.0

    elif H < 0.6:
        # Градиент от темно-зеленого (0, 0.3, 0) до светло-зеленого (0.6, 1.0, 0.6)
        t = (H - 0.3) / 0.3  # Нормализуем в [0, 1) для интерполяции
        # Темно-зеленый -> светло-зеленый
        R = 0.3 * t  # от 0 до 0.6
        G = 0.3 + 0.5 * t  # от 0.3 до 1.0
        B = 0.3 * t  # от 0 до 0.6

    elif H < 0.7:
        # Градиент от темно-зеленого (0.7, 0.7, 0.3) до светло-зеленого (0.8, 0.8, 0.5)
        t = (H - 0.5) / 0.2  # Нормализуем в [0, 1) для интерполяции
        # Темно-зеленый -> светло-зеленый
        R = 0.4 + 0.4 * t  # от 0 до 0.6
        G = 0.4 + 0.4 * t  # от 0.3 до 1.0
        B = 0.5 * t  # от 0 до 0.6
    else:
        # Градиент от темно-серого (0.1, 0.1, 0.1) до светло-серого (0.5, 0.5, 0.5)
        t = ((H - 0.7) / 0.3) ** 6  # Нормализуем в [0, 1] для интерполяции
        # Темно-серый -> светло-серый
        R = 0.2 + 0.3 * t  # от 0.3 до 0.9
        G = 0.2 + 0.3 * t  # от 0.3 до 0.9
        B = 0.2 + 0.3 * t  # от 0.3 до 0.9

    return [np.uint8(R * 255), np.uint8(G * 255), np.uint8(B * 255)]


def heightmap_to_png(Hmap):
    t = []
    for i in Hmap:
        k = []
        for j in i:
            k.append(height_to_color(j))
        t.append(k)
    img_array = np.array(t)
    img_array = img_array[::-1, ...]
    image = Image.fromarray(img_array, mode='RGB')
    return image


def fossils_to_png(fossils):
    palette = {
        0: [0, 0, 0, 0],  # Полностью прозрачный
        1: [50, 50, 50, 128],  # Тёмно-серый, полупрозрачный
        2: [184, 115, 51, 180],  # Медно-рыжий, полупрозрачный
        3: [40, 0, 50, 200],  # Угольно-чёрный с фиолетовым, полупрозрачный
        4: [200, 255, 0, 160]  # Ядовито-зелёно-жёлтый, полупрозрачный
    }
    height, width = fossils.shape
    rgb_array = np.zeros((height, width, 4), dtype=np.uint8)
    for value, color in palette.items():
        mask = (fossils == value)
        rgb_array[mask] = color
    rgb_array = rgb_array[::-1]
    img = Image.fromarray(rgb_array, mode='RGBA')
    return img


def get_uniform_points_adaptive(mask, min_distance=5, max_points=6000):
    y_coords, x_coords = np.where(mask)
    if len(y_coords) == 0:
        return np.array([])
    if len(y_coords) <= max_points:
        return np.column_stack([y_coords, x_coords])
    points = []
    indices = np.arange(len(y_coords))
    np.random.shuffle(indices)
    from scipy.spatial import cKDTree
    all_points = np.column_stack([y_coords, x_coords])
    selected_indices = [indices[0]]
    points.append(all_points[indices[0]])
    tree = cKDTree([all_points[indices[0]]])
    for idx in indices[1:]:
        point = all_points[idx]
        dist, _ = tree.query(point, k=1)
        if dist > min_distance:
            selected_indices.append(idx)
            points.append(point)
            tree = cKDTree(all_points[selected_indices])
        if len(points) >= max_points:
            break
    points.sort(key=lambda a: a[0], reverse=True)
    return np.array(points)


def generation_world_map(N, M, lenght, rt, m, rad, M1, lenght1, rt1, m1, rad1, s):
    set_seed(s)

    mapp = get_small_land(N)
    mapp = np.array(gaussian_filter(mapp, sigma=10))
    mapp = add_stones(mapp, M1, lenght1, rt1, m1, rad1)
    mapp = np.array(gaussian_filter(mapp, sigma=5))
    mapp = add_rivers(mapp, M, lenght, rt, m, rad)

    land_mask = get_big_land_mask(N)

    mapp = np.where(land_mask == 0, 0, mapp)
    mapp = np.array(gaussian_filter(mapp, sigma=1))

    fossils = get_fossils_mask(N)
    fossils = np.where(0.3 > mapp, 0, fossils)
    fossils = np.where(0.7 < mapp, 0, fossils)
    forest_mask = get_forest_mask(N)
    forest_mask = np.where(land_mask == 0, 0, forest_mask)
    forest_mask = np.where(mapp > 0.5, 0, forest_mask)
    forest_mask = np.where(mapp < 0.45, 0, forest_mask)

    mapp = np.kron(mapp, np.ones((2, 2)))
    mapp = np.array(gaussian_filter(mapp, sigma=2))
    mapp = np.kron(mapp, np.ones((2, 2)))
    mapp = np.array(gaussian_filter(mapp, sigma=2))

    fossils = np.kron(fossils, np.ones((4, 4)))

    forest_mask = np.kron(forest_mask, np.ones((4, 4)))
    forest = get_uniform_points_adaptive(forest_mask)

    image_land = heightmap_to_png(mapp)
    image_fossils = fossils_to_png(fossils)
    return image_land, image_fossils, mapp, fossils, forest


basic = (512, 3, 20, 0.09, 30, 2, 3, 10, 0.2, 50, 7.5)
