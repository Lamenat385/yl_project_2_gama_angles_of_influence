import numpy as np

from src.politic.builds.build import Build, FM_Build


class City(Build):
    def __init__(self, coords, nation, type_data, id=None):
        super().__init__(coords, nation, type_data, id)


class Factory(Build):
    def __init__(self, coords, nation, type_data, id=None):
        super().__init__(coords, nation, type_data, id)


class Farm(FM_Build):
    def __init__(self, coords, nation, type_data, id=None):
        super().__init__(coords, nation, type_data, id)

    def get_fruitfulness(self, mapp):
        rows, cols = mapp.shape
        c0, r0 = self.coordinates
        radius = 25
        r_start = max(0, r0 - radius)
        r_end = min(rows, r0 + radius + 1)
        c_start = max(0, c0 - radius)
        c_end = min(cols, c0 + radius + 1)
        sub_arr = mapp[r_start:r_end, c_start:c_end]
        r_indices = np.arange(r_start, r_end) - r0
        c_indices = np.arange(c_start, c_end) - c0
        r_grid, c_grid = np.meshgrid(r_indices, c_indices, indexing='ij')
        distances_sq = r_grid ** 2 + c_grid ** 2
        mask = distances_sq <= radius ** 2
        values = sub_arr[mask]
        return np.count_nonzero((values > 0.6) & (values < 0.3)) / radius ** 2 * 3.14


class Mine(FM_Build):
    def __init__(self, coords, nation, type_data, id=None):
        super().__init__(coords, nation, type_data, id)

    def get_fruitfulness(self, mapp):
        rows, cols = mapp.shape
        c0, r0 = self.coordinates
        radius = 20
        r_start = max(0, r0 - radius)
        r_end = min(rows, r0 + radius + 1)
        c_start = max(0, c0 - radius)
        c_end = min(cols, c0 + radius + 1)
        sub_arr = mapp[r_start:r_end, c_start:c_end]
        r_indices = np.arange(r_start, r_end) - r0
        c_indices = np.arange(c_start, c_end) - c0
        r_grid, c_grid = np.meshgrid(r_indices, c_indices, indexing='ij')
        distances_sq = r_grid ** 2 + c_grid ** 2
        mask = distances_sq <= radius ** 2
        values = sub_arr[mask]
        return np.count_nonzero(values == int(self.type_data[-1])) / radius ** 2 * 3.14
