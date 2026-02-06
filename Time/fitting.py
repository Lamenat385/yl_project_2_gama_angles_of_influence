import numpy as np
from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import json
import lightgbm as lgb
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
# ===== 1. ГЕНЕРАЦИЯ ОБУЧАЮЩИХ ДАННЫХ =====

def pon_gen(field):
    mask = (field >= 0.3) & (field <= 0.6)

    def gen_cluster(cx, cy, n_min, n_max):
        n = np.random.randint(n_min, n_max + 1)
        pts = np.random.normal([cx, cy], 5, (n, 2))

        # 1. Обрезаем координаты до границ [0, 99] ДО индексации маски
        pts = np.clip(pts, 0, 99).astype(int)

        # 2. Фильтруем по маске допустимых клеток
        valid = mask[pts[:, 0], pts[:, 1]]
        pts = pts[valid]

        return pts if pts.size else np.empty((0, 2), dtype=int)

    centers = np.random.randint(15, 85, (4, 2))
    while min(np.hypot(*(centers[i] - centers[j])) for i in range(4) for j in range(i + 1, 4)) < 30:
        centers = np.random.randint(15, 85, (4, 2))

    own = gen_cluster(*centers[0], 12, 20)
    enemy = np.vstack([gen_cluster(*centers[i], 5, 12) for i in range(1, 4)])
    enemy = np.unique(enemy, axis=0) if enemy.size else np.empty((0, 2))
    return np.round(own).astype(int), np.round(enemy).astype(int)

def bal_G(bal):
    """Возвращает тип здания (0-10) с учётом баланса ресурсов"""
    best_score = -np.inf
    best_idx = 0

    for i, building in enumerate(BUILDING_DATA):
        # Преобразуем словари в массивы длины 12
        need = []
        out = []
        for v in building["need_resources"].values():
            need.append(v)
        for v in building["out_resources"].values():
            out.append(v)
        need = np.array(need)
        out = np.array(out)

        # ПРАВИЛЬНЫЙ РАСЧЁТ: новый баланс = текущий - потребление + производство
        new_bal = bal - need + out

        # Метрика: минимизируем дефицит (сумма отрицательных балансов)
        # Чем меньше дефицит → тем выше скор
        deficit = abs(np.sum(np.minimum(new_bal, 0)))  # сумма отрицательных значений
        score = -deficit  # инвертируем: меньше дефицита → выше скор

        if score > best_score:
            best_score = score
            best_idx = i

    # Добавляем 10% случайности для разнообразия данных
    if np.random.rand() < 0.1:
        return np.random.randint(0, len(BUILDING_DATA))

    return best_idx

from tqdm import tqdm


def generate():
    X, y_score, y_type = [], [], []  # ← ДВА целевых массива
    total_combinations = 10 * 18 * 5 * 10 * 10  # секторы × балансы × агрессия × экспансия
    cells_per_combination = 100  # контроль объёма
    pbar = tqdm(total=total_combinations, desc="Генерация данных")

    for i in range(10):
        for j in range(18):
            h = np.load(f'r/{i}_{j}.npy')
            r = [np.load(f'r/{i}_{j}_{k}.npy') for k in range(4)]
            mask_valid = (h >= 0.3) & (h <= 0.6)

            for _ in range(5):
                bal = np.random.uniform(-50, 50, 12)
                own, enemy = pon_gen(h)

                # Маска занятых клеток
                occupied = np.zeros_like(h, dtype=bool)
                pts = []
                if own.size: pts.append(own)
                if enemy.size: pts.append(enemy)
                if pts:
                    all_pts = np.vstack(pts)
                    all_pts = np.clip(np.round(all_pts).astype(int), 0, 99)
                    occupied[all_pts[:, 0], all_pts[:, 1]] = True

                for agres in range(1, 11):
                    agression = 1.0 / agres
                    for expan in range(1, 11):
                        expantion = 1.0 / expan

                        ys, xs = np.where(mask_valid & ~occupied)
                        if xs.size == 0:
                            pbar.update(1)
                            continue

                        # Расстояния до точек
                        dist_own = np.full(xs.shape, 30.0)
                        if own.size:
                            dist_own = np.min([np.hypot(xs - x, ys - y) for x, y in own], axis=0)

                        dist_enemy = np.full(xs.shape, 30.0)
                        if enemy.size:
                            dist_enemy = np.min([np.hypot(xs - x, ys - y) for x, y in enemy], axis=0)

                        # === ТИП ЗДАНИЯ — ОДИН НА ВСЮ ИТЕРАЦИЮ ===
                        type_pred = bal_G(bal)  # ← вычисляем ОДИН раз

                        # Бонусы по типу здания
                        D = np.ones_like(xs, dtype=float)
                        if 6 <= type_pred <= 9:  # ресурсы 0-3
                            D = r[type_pred - 6][ys, xs]
                        elif type_pred == 10:  # ферма — высота ~0.45
                            D = 1.0 - np.abs(h[ys, xs] - 0.45)

                        # Скоринг
                        penalty = 1.0 + np.abs(0.45 - h[ys, xs]) * 10
                        scores = ((25/(dist_own+1) * (1.0 / (expantion * 10)) +
                                   dist_enemy * (1.0 / (agression * 10))) / penalty) * D

                        # Сэмплирование клеток
                        if xs.size > cells_per_combination:
                            idxs = np.random.choice(xs.size, cells_per_combination, replace=False)
                        else:
                            idxs = np.arange(xs.size)

                        # Сохраняем ДАННЫЕ + СКОР + ТИП для каждой клетки
                        for idx in idxs:
                            feats = [
                                h[ys[idx], xs[idx]],
                                *[m[ys[idx], xs[idx]] for m in r],
                                *bal.tolist(),
                                dist_own[idx],
                                dist_enemy[idx],
                                agression,
                                expantion
                            ]
                            X.append(feats)
                            y_score.append(float(scores[idx]))
                            y_type.append(int(type_pred))  # ← сохраняем тип

                        pbar.update(1)

    pbar.close()
    return np.array(X), np.array(y_score), np.array(y_type)
# ===== 2. ОБУЧЕНИЕ МОДЕЛЕЙ =====
class Builder:
    def __init__(self, X, y_coord, y_type):
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X.astype(np.float32))

        # 2. Разделение на train/valid
        X_train, X_valid, y_coord_train, y_coord_valid, y_type_train, y_type_valid = train_test_split(
            X_scaled, y_coord, y_type,
            test_size=0.1,
            random_state=42
        )

        # === РЕГРЕССОР для координат ===
        self.model_coord = lgb.LGBMRegressor(
            n_estimators=300,
            max_depth=12,
            min_child_samples=3,  # ≈ min_samples_split в RF
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            device='gpu',  # ← ВКЛЮЧАЕТ GPU (RTX 3060)
            gpu_platform_id=0,
            gpu_device_id=0,
            n_jobs=6,  # 6 ядер Ryzen
            random_state=42,
            verbosity=1  # ← вывод в конструкторе (не в fit!)
        )
        self.model_coord.fit(
            X_train, y_coord_train,
            eval_set=[(X_valid, y_coord_valid)],
            callbacks=[
                lgb.early_stopping(20, verbose=True),  # ранняя остановка
                lgb.log_evaluation(10)  # вывод каждые 10 итераций
            ]
        )

        # === КЛАССИФИКАТОР для типа ===
        self.model_type = lgb.LGBMClassifier(
            n_estimators=300,
            max_depth=12,
            min_child_samples=3,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            device='gpu',  # ← GPU
            gpu_platform_id=0,
            gpu_device_id=0,
            n_jobs=6,
            random_state=42,
            class_weight='balanced',  # ← встроенная балансировка классов
            verbosity=1
        )
        self.model_type.fit(
            X_train, y_type_train,
            eval_set=[(X_valid, y_type_valid)],
            callbacks=[
                lgb.early_stopping(20, verbose=True),
                lgb.log_evaluation(10)
            ]
        )

    def recommend(self, h, r, bal, own_pts, enemy_pts, agression=1.0, expantion=1.0):
        """
        Рекомендует оптимальную клетку и тип постройки.

        Параметры:
            visualize (bool): если True — отобразить тепловую карту скоров

        Возвращает:
            best_coord: (y, x) координаты лучшей клетки или None
            best_type: строка с типом постройки или None
            score_map: матрица скоров размером с карту (NaN для занятых/неподходящих клеток)
        """
        # 1. Собираем фичи для всех свободных клеток (векторизованно)
        occupied = np.zeros_like(h, dtype=bool)
        if own_pts.size:
            occupied[own_pts[:, 0], own_pts[:, 1]] = True
        if enemy_pts.size:
            occupied[enemy_pts[:, 0], enemy_pts[:, 1]] = True

        # Фильтр по высоте: только клетки с h ∈ [0.3, 0.6]
        valid_mask = ~occupied & (h >= 0.3) & (h <= 0.6)
        ys, xs = np.where(valid_mask)

        # Расстояния до своих точек
        dist_own = np.full(xs.shape, 30.0, dtype=np.float32)
        if own_pts.size:
            dist_own = np.min([np.hypot(xs - x, ys - y) for x, y in own_pts], axis=0)

        # Расстояния до точек противника
        dist_enemy = np.full(xs.shape, 30.0, dtype=np.float32)
        if enemy_pts.size:
            dist_enemy = np.min([np.hypot(xs - x, ys - y) for x, y in enemy_pts], axis=0)

        # Матрица фичей для всех валидных клеток
        feats_matrix = np.column_stack([
            h[ys, xs],
            *[m[ys, xs] for m in r],
            np.tile(bal, (xs.size, 1)),
            dist_own,
            dist_enemy,
            np.full(xs.size, agression, dtype=np.float32),
            np.full(xs.size, expantion, dtype=np.float32)
        ])

        # 2. Предсказываем "полезность" клеток (ваша модель возвращает скор для каждой клетки)
        scores = self.model_coord.predict(feats_matrix.astype(np.float32))

        # 3. Создаём полную карту скоров (размером с исходную карту)
        score_map = np.full_like(h, np.nan, dtype=np.float32)
        score_map[ys, xs] = scores  # Заполняем только валидные клетки

        # 4. Выбираем лучшую клетку
        best_idx = np.argmax(scores)
        best_coord = (int(ys[best_idx]), int(xs[best_idx]))

        # 5. Предсказываем тип постройки для лучшей клетки
        best_feats = feats_matrix[best_idx:best_idx + 1]
        best_type_idx = self.model_type.predict(best_feats.astype(np.float32))[0]

        types = ['city1', 'electry1', 'electry2', 'factory1', 'factory2', 'factory3',
                 'mine1', 'mine2', 'mine3', 'mine4', 'farm1']
        best_type = types[int(best_type_idx)]

        return best_coord, best_type, score_map


# # ===== 4. ПРИМЕР =====
#
# # X, y_coord, y_type = generate()
# #
# # np.save('X.npy', X)
# # np.save('y_coord.npy', y_coord)
# # np.save('y_type.npy', y_type)
#
# X = np.load('X.npy')
# y_coord = np.load('y_coord.npy')
# y_type = np.load('y_type.npy')
# print("Распределение типов в данных:", np.bincount(y_type))
# # build = Builder(X, y_coord, y_type)
# import joblib
# # joblib.dump(build, 'builder.joblib')
#
# build = joblib.load('../src/politic/bots/builder.joblib')
#
# # 1. Посмотрите на распределение целевой переменной
# print("Статистика y_coord:")
# print(f"  Среднее: {y_coord.mean():.2f}")
# print(f"  Стандартное отклонение: {y_coord.std():.2f}")
# print(f"  Диапазон: [{y_coord.min():.2f}, {y_coord.max():.2f}]")
#
# # 2. Сравните с базовой моделью (предсказание среднего)
#
# def plot_feature_importance(model, feature_names, title="Важность признаков", top_n=15):
#     """Отображает топ-N важных признаков горизонтальным барплотом"""
#     importances = model.feature_importances_
#     indices = np.argsort(importances)[::-1][:top_n]  # топ-N индексов
#
#     plt.figure(figsize=(8, min(6, top_n * 0.4)))
#     plt.barh(range(len(indices)), importances[indices][::-1], color='steelblue')
#     plt.yticks(range(len(indices)), [feature_names[i] for i in indices][::-1])
#     plt.xlabel('Важность')
#     plt.title(title)
#     plt.gca().invert_yaxis()  # самый важный сверху
#     plt.tight_layout()
#     plt.show()
#
#
# # === ИСПОЛЬЗОВАНИЕ ===
# # Названия ваших признаков (должны соответствовать порядку в X_train)
# feature_names = [
#     'height',
#     'res0', 'res1', 'res2', 'res3',
#     *[f'bal{i}' for i in range(12)],
#     'dist_own', 'dist_enemy',
#     'agression', 'expantion'
# ]
#
# # Для модели координат
# # plot_feature_importance(build.model_coord, feature_names, "Важность признаков: Координаты")
# #
# # # Для модели типа
# # plot_feature_importance(build.model_type, feature_names, "Важность признаков: Тип точки")
#
# h = np.load(f'r/{8}_{5}.npy')  # исправлено: h/ вместо r/
# r = [np.load(f'r/{8}_{5}_{k}.npy') for k in range(4)]
# bal = np.random.uniform(-50, 50, 12)
# print(bal)
# own, enemy = pon_gen(h)
#
# coord, ptype, scores = build.recommend(h, r, bal, own, enemy,0.5,0.1)
# print(ptype)
#
#
#
# fig, axes = plt.subplots(2, 3, figsize=(15, 10))
# axes = axes.flatten()
#
# # 1. Карта высот
# im0 = axes[0].imshow(scores, cmap='terrain')
# axes[0].set_title('Скоры')
# plt.colorbar(im0, ax=axes[0])
#
# # 2-5. Маски ресурсов
# for i in range(4):
#     im = axes[i+1].imshow(r[i], cmap='YlGnBu')
#     axes[i+1].set_title(f'Ресурс {i}')
#     plt.colorbar(im, ax=axes[i+1])
#     axes[i+1].scatter([coord[0]], [coord[1]], c='green', s=50, label='Метка', edgecolors='white', linewidths=1,
#                     marker='X')
#
# # 6. Карта высот + точки (scatter)
# axes[5].imshow(h, cmap='terrain', alpha=0.7)
# axes[5].scatter(own[:, 1], own[:, 0], c='blue', s=50, label='Свои', edgecolors='white', linewidths=1)
# axes[5].scatter(enemy[:, 1], enemy[:, 0], c='red', s=50, label='Чужие', edgecolors='white', linewidths=1)
# axes[5].scatter([coord[0]], [coord[1]], c='green', s=50, label='Метка', edgecolors='white', linewidths=1, marker='X')
# axes[5].set_title('Высота + точки')
# axes[5].legend(loc='upper right')
#
# # Очистка осей и финал
# for ax in axes:
#     ax.set_xticks([])
#     ax.set_yticks([])
#
# plt.tight_layout()
# plt.show()