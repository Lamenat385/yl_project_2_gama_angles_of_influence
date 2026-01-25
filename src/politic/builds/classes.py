import numpy as np

from src.politic.builds.build import Build, FM_Build


class City(Build):
    def __init__(self, coords, nation, type_data, id=None):
        super().__init__(coords, nation, type_data, id)


class Factory(Build):
    def __init__(self, coords, nation, type_data, id=None):
        super().__init__(coords, nation, type_data, id)

class Electry(Build):
    def __init__(self, coords, nation, type_data, id=None):
        super().__init__(coords, nation, type_data, id)

class Lab(Build):
    def __init__(self, coords, nation, type_data, id=None):
        super().__init__(coords, nation, type_data, id)

class Port(Build):
    def __init__(self, coords, nation, type_data, id=None):
        super().__init__(coords, nation, type_data, id)

class Artillery(Build):
    def __init__(self, coords, nation, type_data, id=None):
        super().__init__(coords, nation, type_data, id)

class Farm(FM_Build):
    def __init__(self, coords, nation, type_data, id=None):
        super().__init__(coords, nation, type_data, id)

    def get_fruitfulness(self, mapp):
        rows, cols = mapp.shape
        c0, r0 = self.coordinates  # x, y (столбец, строка)
        radius = 20
        r_start = int(max(0, r0 - radius))
        r_end = int(min(rows, r0 + radius + 1))
        c_start = int(max(0, c0 - radius))
        c_end = int(min(cols, c0 + radius + 1))

        # Вычисляем локальные координаты центра внутри вырезанного фрагмента
        local_r0 = r0 - r_start
        local_c0 = c0 - c_start

        # Генерируем сетку индексов для фрагмента
        rr, cc = np.indices((r_end - r_start, c_end - c_start))
        dist_sq = (rr - local_r0) ** 2 + (cc - local_c0) ** 2
        mask = dist_sq <= radius ** 2

        values = mapp[r_start:r_end, c_start:c_end][mask]
        count = np.count_nonzero((values < 0.6) & (values > 0.3))

        # Используем точное значение pi и избегаем деления на ноль
        area = np.pi * radius ** 2
        return count / area if area > 0 else 0.0


class Mine(FM_Build):
    def __init__(self, coords, nation, type_data, id=None):
        super().__init__(coords, nation, type_data, id)

    def get_fruitfulness(self, mapp):
        rows, cols = mapp.shape
        c0, r0 = self.coordinates  # x, y (столбец, строка)
        radius = 15
        r_start = int(max(0, r0 - radius))
        r_end = int(min(rows, r0 + radius + 1))
        c_start = int(max(0, c0 - radius))
        c_end = int(min(cols, c0 + radius + 1))

        # Вычисляем локальные координаты центра внутри вырезанного фрагмента
        local_r0 = r0 - r_start
        local_c0 = c0 - c_start

        # Генерируем сетку индексов для фрагмента
        rr, cc = np.indices((r_end - r_start, c_end - c_start))
        dist_sq = (rr - local_r0) ** 2 + (cc - local_c0) ** 2
        mask = dist_sq <= radius ** 2

        # Считаем совпадения с целевым значением
        target = int(self.type_data[-1])
        count = np.count_nonzero(mapp[r_start:r_end, c_start:c_end][mask] == target)

        # Используем точное значение pi и избегаем деления на ноль
        area = np.pi * radius ** 2
        return count / area if area > 0 else 0.0
