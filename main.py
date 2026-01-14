import arcade
from src.windows.base_window import BaseWindow
from src.generate_map.generate_map import generation_world_map, basic
import numpy as np
from random import randint


if __name__ == "__main__":
    # Создаем главное окно
    # asu = basic + tuple([randint(0, 100)])
    # o, f, a, b, c = generation_world_map(*asu)
    # f.save("data/saves/1/fossils.png")
    # o.save("data/saves/1/land.png")
    # np.save("data/saves/1/land.npy", a)
    # np.save("data/saves/1/fossils.npy", b)
    # np.save("data/saves/1/forest.npy", c)

    window = BaseWindow()

    # Показываем стартовый экранa
    window.switch_view("start")

    # Запускаем игровой цикл
    arcade.run()
