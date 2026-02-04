
import numpy as np
from shapely.geometry import box, Polygon, MultiPoint
from shapely.ops import unary_union
from scipy.spatial import cKDTree

def build_boundary(points, side=1.0, alpha=None):
    """
    Быстрая граница:
    • < 3 точек → квадраты
    • ≥ 3 точек → α-оболочка с фиксированным или эвристическим α
    """
    # Нормализация входа в ndarray
    if isinstance(points, MultiPoint):
        pts = np.array([[p.x, p.y] for p in points.geoms])
    elif hasattr(points, 'x') and hasattr(points, 'y'):  # Shapely Point
        pts = np.array([[points.x, points.y]])
    else:
        pts = np.asarray(points, dtype=float)
        if pts.ndim == 1 and pts.size == 2:
            pts = pts.reshape(1, -1)

    n = len(pts)
    if n == 0:
        raise ValueError("Пустой набор точек")
    if n < 3:
        squares = [box(x - side/2, y - side/2, x + side/2, y + side/2)
                   for x, y in pts]
        return unary_union(squares) if n > 1 else squares[0]

    # Эвристика α: обратно пропорциональна среднему расстоянию до 2-го соседа
    if alpha is None:
        tree = cKDTree(pts)
        dists, _ = tree.query(pts, k=3)  # 1-й = 0 (сама точка), 2-й и 3-й соседи
        avg_dist = np.mean(dists[:, 2])  # расстояние до 2-го соседа
        alpha = 1.0 / max(avg_dist, 1e-6) * 0.8  # коэффициент подстройки

    try:
        import alphashape
        boundary = alphashape.alphashape(pts, alpha)
        if boundary.is_empty or boundary.area < 1e-9:
            raise ValueError("Пустая оболочка")
        return boundary
    except Exception:
        # Резерв: выпуклая оболочка (быстро)
        from scipy.spatial import ConvexHull
        hull = ConvexHull(pts)
        return Polygon(pts[hull.vertices])


class Territory_manager:
    def __init__(self,manager):
        self.manager=manager
    def nation_from_point(self,point):
        for i in self.manager.nations_set:
            if i.area.contains(*point):
                return i
        return None
    def area_from_nation(self,nation):
        return nation.area.area
    def update(self):
        p={}
        for i in self.manager.id_to_build.values():
            if i.nation not in p:
                p[i.nation]=[i.coordinates]
            else:
                p[i.nation].append(i.coordinates)
        for i in p:
            i.area=build_boundary(p[i])