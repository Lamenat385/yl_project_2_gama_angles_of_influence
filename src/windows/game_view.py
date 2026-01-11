import arcade
import numpy as np
from random import choice

from src.registry import reg


class GameView(arcade.View):
    """Основной игровой view с картой высот и камерой"""

    def __init__(self, window):
        super().__init__(window)
        self.trees=np.load("data/saves/1/forest.npy")
        self.height_map = np.load("data/saves/1/land.npy")  # 2D массив высот NxN
        self.N = len(self.height_map)
        self.cell_size_percent = 1.25
        self.cell_size = int(self.window.height * self.cell_size_percent / 100)
        self.map_width = self.N * self.cell_size
        self.map_height = self.N * self.cell_size
        self.world_texture = arcade.load_texture("data/saves/1/land.png")
        self.fossils_texture = arcade.load_texture("data/saves/1/fossils.png")
        self.fossils_view=True
        self.fossils_sprite=None
        # Создаем спрайт

        # Создаем камеру (используем SimpleCamera для простоты)
        # SimpleCamera предоставляет базовый функционал камеры
        self.camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()

        # Позиция камеры (центр экрана в мировых координатах)
        self.camera_x = self.map_width / 2
        self.camera_y = self.map_height / 2
        self.camera_speed = self.map_width / 6

        # Управление камерой
        self.camera_moving = {
            'up': False, 'down': False, 'left': False, 'right': False
        }

        # Используем спрайты для отрисовки сетки
        self.sprite_list = None
        self.create_shapes()

    def create_shapes(self):
        """Создание спрайтов для отрисовки сетки"""
        self.sprite_list = arcade.SpriteList()
        sprite = arcade.Sprite()
        sprite.texture = self.world_texture
        sprite.center_x = self.map_width / 2
        sprite.center_y = self.map_height / 2
        sprite.scale = self.cell_size
        self.sprite_list.append(sprite)
        for y,x in self.trees:
            sprite = arcade.Sprite()
            sprite.texture = choice((reg.images["resources/tree1.png"],reg.images["resources/tree2.png"]))
            sprite.center_x = x*self.cell_size
            sprite.center_y = y*self.cell_size
            sprite.scale = 10*self.cell_size/128
            self.sprite_list.append(sprite)
        self.fossils_sprite = arcade.Sprite()
        self.fossils_sprite.texture = self.fossils_texture
        self.fossils_sprite.center_x = self.map_width / 2
        self.fossils_sprite.center_y = self.map_height / 2
        self.fossils_sprite.scale = self.cell_size

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.sprite_list.draw(pixelated=True)
        self.gui_camera.use()
        self.draw_gui()

    def draw_gui(self):
        """Отрисовка GUI элементов"""
        arcade.draw_text(
            f"Камера: ({int(self.camera_x)}, {int(self.camera_y)})",
            10, self.window.height - 30,
            arcade.color.WHITE, 16
        )

        arcade.draw_text(
            f"Карта: {self.N}x{self.N}, Ячейка: {self.cell_size}px",
            10, self.window.height - 60,
            arcade.color.WHITE, 16
        )

        arcade.draw_text(
            "WASD - движение камеры | ESC - меню | Q - выход",
            10, 10,
            arcade.color.WHITE, 16
        )

    def on_update(self, delta_time):
        if self.fossils_sprite in self.sprite_list and not self.fossils_view:
            self.sprite_list.remove(self.fossils_sprite)
        elif self.fossils_sprite not in self.sprite_list and self.fossils_view:
            self.sprite_list.append(self.fossils_sprite)
        speed = self.camera_speed * delta_time
        new_camera_x = self.camera_x
        new_camera_y = self.camera_y

        if self.camera_moving['up']:
            new_camera_y += speed
        if self.camera_moving['down']:
            new_camera_y -= speed
        if self.camera_moving['left']:
            new_camera_x -= speed
        if self.camera_moving['right']:
            new_camera_x += speed

        self.camera.position = arcade.math.lerp_2d(  # Изменяем позицию камеры
            self.camera.position,
            (new_camera_x,new_camera_y),
            0.13,  # Плавность следования камеры
        )
        self.camera_x=new_camera_x
        self.camera_y = new_camera_y
    def on_key_press(self, key, modifiers):
        if key == arcade.key.W:
            self.camera_moving['up'] = True
        elif key == arcade.key.S:
            self.camera_moving['down'] = True
        elif key == arcade.key.A:
            self.camera_moving['left'] = True
        elif key == arcade.key.D:
            self.camera_moving['right'] = True
        elif key == arcade.key.V:
            self.fossils_view= not self.fossils_view
        elif key == arcade.key.Q:
            self.window.close()
        elif key == arcade.key.ESCAPE:
            self.window.switch_view("main_menu")

    def on_key_release(self, key, modifiers):
        if key == arcade.key.W:
            self.camera_moving['up'] = False
        elif key == arcade.key.S:
            self.camera_moving['down'] = False
        elif key == arcade.key.A:
            self.camera_moving['left'] = False
        elif key == arcade.key.D:
            self.camera_moving['right'] = False

    def on_resize(self, width, height):
        super().on_resize(width, height)

        # Пересчитываем размеры
        self.cell_size = int(height * self.cell_size_percent / 100)
        self.map_width = self.N * self.cell_size
        self.map_height = self.N * self.cell_size

        # Обновляем границы камеры

        # Пересоздаем спрайты с новыми размерами
        self.create_shapes()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        zoom_sensitivity = 0.05
        self.camera.zoom += scroll_y * zoom_sensitivity

        # Ограничиваем масштаб
        self.camera.zoom = max(0.05, min(self.camera.zoom, 5.0))
