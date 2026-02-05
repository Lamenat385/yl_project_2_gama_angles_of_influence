import random
from statistics import mode, multimode
import joblib

from src.politic.builds.classes import City, Factory, Mine, Farm, Artillery, Electry
from src.politic.nation import Nation

import numpy as np


def extract_and_downscale(field, points, output_size=100, upscale_factor=4):
    """
    Вырезает квадрат из поля с центром в центроиде точек и уменьшает его в upscale_factor раз.

    Параметры:
        field: np.ndarray размером (2048, 2048)
        points: массив координат [(y1, x1), (y2, x2), ...]
        output_size: итоговый размер после даунскейлинга (по умолчанию 100)
        upscale_factor: коэффициент даунскейлинга (по умолчанию 4 → 400→100)

    Возвращает:
        Массив размером (output_size, output_size)
        Координаты центра облака точек (y, x)
    """
    # 1. Находим центр облака точек
    points = np.array(points)
    center_y = int(round(np.mean(points[:, 0])))
    center_x = int(round(np.mean(points[:, 1])))

    # 2. Вычисляем размер исходного квадрата до даунскейлинга
    src_size = output_size * upscale_factor  # 100 * 4 = 400

    # 3. Границы квадрата 400x400
    half = src_size // 2
    top = center_y - half
    bottom = center_y + half
    left = center_x - half
    right = center_x + half

    # 4. Обрезка по границам поля + дополнение нулями при выходе за край
    top_clipped = max(0, top)
    bottom_clipped = min(field.shape[0], bottom)
    left_clipped = max(0, left)
    right_clipped = min(field.shape[1], right)

    cropped = field[top_clipped:bottom_clipped, left_clipped:right_clipped]

    # Дополнение до полного размера 400x400 при необходимости
    if cropped.shape != (src_size, src_size):
        padded = np.zeros((src_size, src_size), dtype=field.dtype)
        pad_top = max(0, -top)
        pad_left = max(0, -left)
        h, w = cropped.shape
        padded[pad_top:pad_top + h, pad_left:pad_left + w] = cropped
        cropped = padded
    downscaled = cropped.reshape(output_size, upscale_factor,
                                 output_size, upscale_factor).mean(axis=(1, 3))
    return downscaled, (center_y, center_x)


def local_to_global(y_local, x_local, center_y, center_x,
                    output_size=100, upscale_factor=4, method='center'):
    """
    Преобразует координаты из локальной системы (100x100) в глобальные (2048x2048).

    Параметры:
        y_local, x_local: координаты в локальном изображении (0..99)
        center_y, center_x: центр облака точек в глобальных координатах
        output_size: размер локального изображения (по умолчанию 100)
        upscale_factor: коэффициент даунскейлинга (по умолчанию 4)
        method: 'center' (центр блока 4x4) или 'corner' (левый верхний угол)

    Возвращает:
        (y_global, x_global) — координаты в глобальном поле
    """
    src_size = output_size * upscale_factor  # 400

    # Левый верхний угол исходного квадрата 400x400 в глобальных координатах
    top = center_y - src_size // 2  # center_y - 200
    left = center_x - src_size // 2  # center_x - 200

    # Координата внутри квадрата 400x400 (до даунскейлинга)
    if method == 'center':
        # Центр соответствующего блока 4x4
        y_in_square = y_local * upscale_factor + upscale_factor // 2  # +2
        x_in_square = x_local * upscale_factor + upscale_factor // 2  # +2
    elif method == 'corner':
        # Левый верхний угол блока
        y_in_square = y_local * upscale_factor
        x_in_square = x_local * upscale_factor
    else:
        raise ValueError("method must be 'center' or 'corner'")

    # Глобальные координаты
    y_global = top + y_in_square
    x_global = left + x_in_square

    return int(round(y_global)), int(round(x_global))


def global_to_local(y_global, x_global, center_y, center_x,
                    output_size=100, upscale_factor=4, method='center'):
    """
    Преобразует глобальные координаты (2048x2048) в локальные (100x100).

    Возвращает:
        (y_local, x_local) — координаты в локальном изображении или None, если вне области
    """
    src_size = output_size * upscale_factor  # 400

    # Границы квадрата 400x400 в глобальных координатах
    top = center_y - src_size // 2
    bottom = top + src_size
    left = center_x - src_size // 2
    right = left + src_size

    # Проверка, что точка внутри квадрата
    if not (top <= y_global < bottom and left <= x_global < right):
        return None  # Точка вне вырезанной области

    # Координата внутри квадрата 400x400
    y_in_square = y_global - top
    x_in_square = x_global - left

    # Преобразование в локальные координаты с учётом метода
    if method == 'center':
        y_local = (y_in_square - upscale_factor // 2) / upscale_factor
        x_local = (x_in_square - upscale_factor // 2) / upscale_factor
    elif method == 'corner':
        y_local = y_in_square / upscale_factor
        x_local = x_in_square / upscale_factor
    else:
        raise ValueError("method must be 'center' or 'corner'")

    # Округление до целых индексов локального изображения
    y_local_idx = int(round(y_local))
    x_local_idx = int(round(x_local))

    # Дополнительная проверка границ локального изображения
    if not (0 <= y_local_idx < output_size and 0 <= x_local_idx < output_size):
        return None

    return y_local_idx, x_local_idx


def extract_and_downscale_multiclass(field, center_x, center_y, output_size=100, upscale_factor=4):
    """
    Вырезает квадрат 400x400 из поля с центром в центроиде точек,
    разделяет на 4 булевых маски (значения 1-4) и даунскейлит каждую до 100x100.

    Параметры:
        field: np.ndarray размером (2048, 2048) со значениями 1, 2, 3, 4
        points: массив координат [(y1, x1), (y2, x2), ...]
        output_size: итоговый размер маски после даунскейлинга (по умолчанию 100)
        upscale_factor: коэффициент даунскейлинга (по умолчанию 4 → 400→100)

    Возвращает:
        Список из 4 булевых массивов размером (output_size, output_size):
        [mask_class_1, mask_class_2, mask_class_3, mask_class_4]
        где mask_class_i[y, x] = True, если в соответствующем блоке 4x4 был пиксель со значением i
    """
    # 1. Находим центр облака точек

    # 2. Размер исходного квадрата до даунскейлинга
    src_size = output_size * upscale_factor  # 400

    # 3. Границы квадрата 400x400
    half = src_size // 2
    top = center_y - half
    bottom = center_y + half
    left = center_x - half
    right = center_x + half

    # 4. Обрезка по границам поля + дополнение нулями (фон = 0, не относится к классам 1-4)
    top_clipped = max(0, top)
    bottom_clipped = min(field.shape[0], bottom)
    left_clipped = max(0, left)
    right_clipped = min(field.shape[1], right)

    cropped = field[top_clipped:bottom_clipped, left_clipped:right_clipped]

    # Дополнение до 400x400 нулями (фон)
    if cropped.shape != (src_size, src_size):
        padded = np.zeros((src_size, src_size), dtype=field.dtype)
        pad_top = max(0, -top)
        pad_left = max(0, -left)
        h, w = cropped.shape
        padded[pad_top:pad_top + h, pad_left:pad_left + w] = cropped
        cropped = padded

    # 5. Создаём 4 булевых маски и даунскейлим через логическое ИЛИ по блокам 4x4
    masks = []
    for class_value in range(1, 5):  # значения 1, 2, 3, 4
        # Булева маска для текущего класса
        mask = (cropped == class_value)

        # Даунскейлинг: если хотя бы один пиксель в блоке 4x4 = True → результат = True
        # reshape: (100, 4, 100, 4) → any по осям 1 и 3
        reshaped = mask.reshape(output_size, upscale_factor, output_size, upscale_factor)
        downscaled = reshaped.any(axis=(1, 3))

        masks.append(downscaled)

    return masks  # [mask_1, mask_2, mask_3, mask_4], каждая размером (100, 100)


class Bot:
    def __init__(self, manager, expensive, aggressive, coords):
        self.manager = manager
        self.expensive = expensive
        self.aggressive = aggressive
        self.emotions = {}
        self.builder = joblib.load("src/politic/bots/builder.joblib")
        self.nation = Nation(self.manager, "name", random.randint(0, 3), coords)

    def update_emotions(self, events):
        for i in events:
            if not i["nation"] is self.nation:
                if i["type"] == "build":
                    if self.nation.area.contains(i["coordinates"]):
                        self.emotions[i["nation"]] += self.expensive * (-20)
                    if i["data"] == "artillery":
                        self.emotions[i["nation"]] += 1 / (self.aggressive * 10) * (-10) + self.expensive * (-10)
                elif i["type"] == "destroy":
                    if i["data"].nation is self.nation:
                        self.emotions[i["nation"]] += -30 - 50 * self.aggressive * self.expensive
                elif i["type"] == "trade":
                    if not i["data"] is self.nation and not i["nation"] is self.nation:
                        k = (self.emotions[i["nation"]] + self.emotions[i["data"]]) / 2
                        self.emotions[i["nation"]] = (k + self.emotions[i["nation"]]) / 2
                        self.emotions[i["data"]] = (k + self.emotions[i["data"]]) / 2

    def choice(self):
        own = []
        enemy = []
        groups = []
        for i in self.manager.id_to_build.values():
            if i.nation is self.nation:
                groups.append(i.group)
                own.append(i.coordinates)
            else:
                enemy.append(i.coordinates)
        group = multimode(groups)[0]
        bal = group.resources
        map, cords = extract_and_downscale(self.manager.world_map, own, 100, 4)
        for i in range(len(own)):
            own[i] = global_to_local(*own[i], *cords, 100, 4)
        for i in range(len(enemy)):
            enemy[i] = global_to_local(*enemy[i], *cords, 100, 4)
        r = extract_and_downscale_multiclass(self.manager.fossils, *cords, 100, 4)

        fc, tp, scr = self.builder.recommend(map, r, bal, np.array(own), np.array(enemy), self.aggressive, self.expensive)
        coords = local_to_global(*fc, *cords)
        builds = {
            "city": City,
            "factory": Factory,
            "mine": Mine,
            "farm": Farm,
            "artillery": Artillery,
            "electry": Electry
        }
        b = builds[tp[:-1]](coords, self.nation, tp)
        self.manager.new_build(b)
        dist = 1e9
        g = None
        for k, v in self.manager.id_to_build.items():
            if v.nation is self.nation:
                d = ((v.coordinates[0] - b.coordinates[0]) + (v.coordinates[1] - b.coordinates[1])) * 0.5
                if d < dist:
                    dist = d
                    g = k
        l = (b.id, g)
        self.manager.new_link(l)
