import math
from random import randint, random

import numpy as np


def get_random_border_points_numpy(N, M):
    if N <= 1:
        return [(0, 0)] if M > 0 else []

    total_border = 4 * N - 4
    if M > total_border:
        M = total_border
    top_bottom_rows = np.repeat([0, N - 1], N)
    top_bottom_cols = np.tile(np.arange(N), 2)
    top_bottom = np.column_stack([top_bottom_rows, top_bottom_cols])
    left_right_rows = np.tile(np.arange(1, N - 1), 2)
    left_right_cols = np.repeat([0, N - 1], N - 2)
    left_right = np.column_stack([left_right_rows, left_right_cols])
    all_points = np.vstack([top_bottom, left_right])
    indices = np.random.choice(len(all_points), size=M, replace=False)
    return [tuple(point) for point in all_points[indices]]


def begin_vc(N, M):
    t = N / 2
    d = []
    x = 1 / (t / 2 * (math.sqrt(2) / 25 + 1 / 15))
    for i in get_random_border_points_numpy(N, M):
        v = (i[0], i[1], (t - i[0]) * x + i[0], (t - i[1]) * x + i[1])
        d.append(v)
    return d


def create_vector_relative(initial_vector, ag, new_len):
    x1, y1, x2, y2 = initial_vector

    # Вычисляем угол исходного вектора
    dx_initial = x2 - x1
    dy_initial = y2 - y1
    initial_angle = math.atan2(dy_initial, dx_initial)

    # Преобразуем угол поворота и добавляем к углу исходного вектора
    ag_rad = math.radians(ag)
    total_angle = initial_angle + ag_rad

    # Вычисляем координаты конца нового вектора
    x_new = x2 + new_len * math.cos(total_angle)
    y_new = y2 + new_len * math.sin(total_angle)

    return (int(x2), int(y2), int(x_new), int(y_new))


def make_river(rivers, bg, length, N, rt, m):
    st = [bg]
    for i in range(1, length):
        st.append(create_vector_relative(st[i - 1], randint(-m, m), N / 15))
        if random() < rt and length - i > 1:
            rivers = make_river(rivers, st[i - 1], length - i, N, rt * 0.9, int(m * 1.2))
    opi = st[0][:2]
    for i in range(length):
        st[i] = st[i][2:]
    st = [opi] + st
    rivers.append(st)
    return rivers


def make_rives(map, M, length, rt, m):
    rivers = []
    N = map.shape[0]
    beg = begin_vc(N, M)
    for j in beg:
        rivers = make_river(rivers, j, length, N, rt, m)
    return rivers


def mark_cells_near_polyline(field, p, f, radius=5):
    if not isinstance(field, np.ndarray):
        result = np.array(field, dtype=float)
    else:
        result = field.copy()

    N = result.shape[0]

    g = []
    for i in p:
        if 0 <= i[0] <= N and 0 <= i[1] <= N:
            g.append(i)
    p = g

    if len(p) < 1:
        return result

    # Преобразуем все точки в целые числа
    int_points = []
    for point in p:
        if isinstance(point, (tuple, list)) and len(point) >= 2:
            x, y = point
            # Округляем до ближайшего целого
            int_points.append((int(round(x)), int(round(y))))

    if len(int_points) < 1:
        return result

    # Создаем сетку индексов один раз для оптимизации
    indices = np.arange(N)
    xx, yy = np.meshgrid(indices, indices, indexing='ij')

    # Создаем маску для всего поля
    mask = np.zeros((N, N), dtype=bool)

    # Функция для добавления круга в маску
    def add_circle_to_mask(cx, cy):
        # Вычисляем расстояния от всех точек до центра (cx, cy)
        distances_sq = (xx - cx) ** 2 + (yy - cy) ** 2
        # Отмечаем точки внутри радиуса
        mask[distances_sq <= radius ** 2] = True

    # Отмечаем все точки ломаной
    for x, y in int_points:
        if 0 <= x < N and 0 <= y < N:
            add_circle_to_mask(x, y)

    # Если есть несколько точек, добавляем промежуточные
    if len(int_points) > 1:
        for i in range(len(int_points) - 1):
            x1, y1 = int_points[i]
            x2, y2 = int_points[i + 1]

            # Количество промежуточных точек зависит от расстояния
            dist = max(abs(x2 - x1), abs(y2 - y1))
            steps = max(1, int(dist // 2))  # Шаг в 2 клетки для оптимизации

            if steps > 0:
                for t in np.linspace(0, 1, steps + 1):
                    x = int(round(x1 + (x2 - x1) * t))
                    y = int(round(y1 + (y2 - y1) * t))
                    if 0 <= x < N and 0 <= y < N:
                        add_circle_to_mask(x, y)

    # Применяем маску
    result[mask] = f

    return result


def add_rivers(mapp, M, length, rt, m, rad):
    d = make_rives(mapp, M, length, rt, m)
    t = mapp
    for i in d:
        t = mark_cells_near_polyline(t, i, 0, radius=rad)
    return t
