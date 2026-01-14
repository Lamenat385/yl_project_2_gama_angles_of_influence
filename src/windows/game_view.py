import arcade
import numpy as np
from random import choice


from src.politic.builds.classes import Factory, City, Mine, Farm
from src.politic.manager import Manager
from src.registry import reg
from src.player import Player

class GameView(arcade.View):
    """Основной игровой view с картой высот и камерой"""

    def __init__(self, window):
        super().__init__(window)
        self.roads = []
        self.window.set_mouse_visible(False)
        self.button_textures = [
            reg.images["resources/city.png"],
            reg.images["resources/factory.png"],
            reg.images["resources/mine.png"],
            reg.images["resources/farm.png"],
            reg.images["resources/lab.png"],
            reg.images["resources/port.png"],
            reg.images["resources/artillery.png"],
        ]
        self.bN=len(self.button_textures)
        self.show_selection_panel = False
        self.selected_button = None
        self.hovered_option = -1
        self.option_is_selected = False

        self.cursor_x = 0
        self.cursor_y = 0
        self.cursor_texture = reg.images["resources/capital.png"]

        self.trees = np.load("data/saves/1/forest.npy")
        self.height_map = np.load("data/saves/1/land.npy")  # 2D массив высот NxN

        self.groups_manager = Manager(self.height_map)
        self.player = Player("test",self.groups_manager,"Circle",(100,200))

        self.N = len(self.height_map)
        self.cell_size_percent = 1.25
        self.cell_size = int(self.window.height * self.cell_size_percent / 100)
        self.map_width = self.N * self.cell_size
        self.map_height = self.N * self.cell_size
        self.world_texture = arcade.load_texture("data/saves/1/land.png")
        self.fossils_texture = arcade.load_texture("data/saves/1/fossils.png")
        self.fossils_view = True
        self.fossils_sprite = None
        # Создаем спрайт

        # Создаем камеру (используем SimpleCamera для простоты)
        # SimpleCamera предоставляет базовый функционал камеры
        self.camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()

        # Позиция камеры (центр экрана в мировых координатах)
        self.camera_x = self.map_width / 2
        self.camera_y = self.map_height / 2
        self.camera_speed = self.map_width / 6
        self.selected_builds=[]
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
        self.update_roads()
        arcade.draw.draw_lines(self.roads,arcade.color.BLACK,self.cell_size*4)
        for j in self.groups_manager.id_to_build.values():
            x,y=j.coordinates
            sprite = arcade.Sprite()
            sprite.texture = reg.images[f"resources/{j.type_data[:-1] if j.type_data[-1].isdigit() else j.type_data}.png"]
            sprite.center_x = x * self.cell_size
            sprite.center_y = y * self.cell_size
            sprite.scale = 15 * self.cell_size / 128
            self.sprite_list.append(sprite)
        for y, x in self.trees:
            sprite = arcade.Sprite()
            sprite.texture = choice((reg.images["resources/tree1.png"], reg.images["resources/tree2.png"]))
            sprite.center_x = x * self.cell_size
            sprite.center_y = y * self.cell_size
            sprite.scale = 10 * self.cell_size / 128
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
        panel_height = int(self.window.height * 0.15)
        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                self.window.width // 2,
                panel_height // 2,
                self.window.width,
                panel_height
            ),
            arcade.color.DARK_GRAY
        )
        sprite_list=arcade.SpriteList()
        # Отрисовка кнопок-картинок на панели (4 квадратные кнопки)
        button_size = int(panel_height * 0.7)  # Размер кнопок - 70% высоты панели
        margin = 20  # Отступ от краев
        spacing = (self.window.width - 2 * margin - self.bN * button_size) // (self.bN+1)  # Равномерное расстояние между кнопками

        for i in range(self.bN):
            button_x = margin + spacing + i * (button_size + spacing) + button_size // 2
            button_y = panel_height // 2

            # Рисуем фон кнопки
            arcade.draw_rect_filled(
                arcade.rect.XYWH(
                    button_x,
                    button_y,
                    button_size,
                    button_size
                ),
                arcade.color.LIGHT_GRAY
            )

            sprite = arcade.Sprite()
            sprite.texture = self.button_textures[i]
            sprite.center_x = button_x
            sprite.center_y = button_y
            sprite.scale = button_size/128
            sprite_list.append(sprite)

        # Отрисовка центральной панели с выбором (если активна)
        if hasattr(self, 'show_selection_panel') and self.show_selection_panel:

            texts=[
                ["Город","Столица"],
                ["Металичесские детали", "Электро-механические платы", "Высоко-точные энерго-вычеслители"],
                ["Чёрные металы", "Цветные металы","Углеводороды","Сверхтяжёлые минералы"],
                ["Ферма"],
                ["Лаборатория"],
                ["Порт"],
                ["Тяжёлая артиллерия", "Сверхтяжёлая артиллерия"],
            ]

            # Полупрозрачный фон
            arcade.draw_rect_filled(
                arcade.rect.XYWH(
                    self.window.width // 2,
                    self.window.height // 2,
                    self.window.width,
                    self.window.height
                ),
                (0, 0, 0, 200)  # Черный с прозрачностью
            )

            # Панель выбора
            panel_width = int(self.window.width * 0.6)
            panel_height_central = int(self.window.height * 0.4)

            arcade.draw_rect_filled(
                arcade.rect.XYWH(
                    self.window.width // 2,
                    self.window.height // 2,
                    panel_width,
                    panel_height_central
                ),
                arcade.color.DARK_SLATE_GRAY
            )

            # 4 варианта выбора
            option_height = panel_height_central // 5
            for i in range(len(texts[self.selected_button])):
                option_y = (self.window.height // 2 + panel_height_central // 2
                            - option_height * (i + 1) + option_height // 2)

                # Кнопка варианта
                arcade.draw_rect_filled(
                    arcade.rect.XYWH(
                        self.window.width // 2,
                        option_y,
                        panel_width - 40,
                        option_height - 10
                    ),
                    arcade.color.LIGHT_GRAY if self.hovered_option != i else arcade.color.GRAY
                )

                # Текст варианта
                arcade.draw_text(
                    texts[self.selected_button][i],
                    self.window.width // 2,
                    option_y,
                    arcade.color.BLACK,
                    18,
                    align="center",
                    anchor_x="center",
                    anchor_y="center"
                )

        # Остальной GUI (ваш существующий код)
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

        sprite = arcade.Sprite()
        sprite.texture = self.cursor_texture
        sprite.center_x = self.cursor_x
        sprite.center_y = self.cursor_y
        sprite.scale = 0.3
        sprite_list.append(sprite)

        sprite_list.draw(pixelated=True)


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
            (new_camera_x, new_camera_y),
            0.13,  # Плавность следования камеры
        )
        self.camera_x = new_camera_x
        self.camera_y = new_camera_y

    def on_mouse_press(self, x, y, button, modifiers):
        self.cursor_x = x
        self.cursor_y = y
        self.cursor_texture=reg.images["resources/capital.png"]
        """Обработка нажатия мыши"""
        # Проверка нажатия на кнопки нижней панели
        if not self.show_selection_panel:
            panel_height = int(self.window.height * 0.15)
            button_size = int(panel_height * 0.7)
            margin = 20
            spacing = (self.window.width - 2 * margin - self.bN * button_size) // (self.bN+1)

            for i in range(self.bN):
                button_x = margin + spacing + i * (button_size + spacing) + button_size // 2
                button_y = panel_height // 2

                # Проверка попадания в кнопку
                if (abs(x - button_x) < button_size // 2 and
                        abs(y - button_y) < button_size // 2):
                    self.show_selection_panel = True
                    self.selected_button = i
                    return

        # Проверка нажатия на варианты в центральной панели
        if self.show_selection_panel:
            panel_width = int(self.window.width * 0.6)
            panel_height_central = int(self.window.height * 0.4)
            option_height = panel_height_central // 5

            for i in range(4):
                option_y = (self.window.height // 2 + panel_height_central // 2
                            - option_height * (i + 1) + option_height // 2)

                # Проверка попадания в вариант
                if (abs(x - self.window.width // 2) < (panel_width - 40) // 2 and
                        abs(y - option_y) < (option_height - 10) // 2):
                    self.on_option_selected(self.selected_button, i)
                    self.show_selection_panel = False
                    return

        if self.option_is_selected:
            self.new_build()

        coords = self.camera.unproject((self.cursor_x, self.cursor_y))

        for i in self.groups_manager.groups_set:
            for j in i.builds_set:
                x,y=j.coordinates
                if j not in self.selected_builds:
                    if (x-15)*self.cell_size<coords.x<(x+15)*self.cell_size and (y-15)*self.cell_size<coords.y<(y+15)*self.cell_size and j.nation is self.player.nation:
                        self.selected_builds.append(j)
                        if len(self.selected_builds)>15:
                            self.selected_builds=self.selected_builds[-15:]

    def on_mouse_motion(self, x, y, dx, dy):
        self.cursor_x = x
        self.cursor_y = y
        """Обработка движения мыши для hover-эффекта"""
        if self.show_selection_panel:
            panel_width = int(self.window.width * 0.6)
            panel_height_central = int(self.window.height * 0.4)
            option_height = panel_height_central // 5

            self.hovered_option = -1
            for i in range(4):
                option_y = (self.window.height // 2 + panel_height_central // 2
                            - option_height * (i + 1) + option_height // 2)

                if (abs(x - self.window.width // 2) < (panel_width - 40) // 2 and
                        abs(y - option_y) < (option_height - 10) // 2):
                    self.hovered_option = i
                    break

    def on_option_selected(self, button_index, option_index):
        """Вызывается при выборе варианта"""
        buttons=["city","factory","mine","farm","lab","port","artillery"]
        if 0 <= button_index < self.bN and 0 <= option_index < 4:
            self.cursor_texture = self.button_textures[button_index]
            self.player.current_choice=buttons[button_index]+str(option_index+1)
            self.option_is_selected = True

    def new_build(self):
        coords=self.camera.unproject((self.cursor_x, self.cursor_y))
        builds={
            "city":City,
            "factory": Factory,
            "mine": Mine,
            "farm": Farm,
        }
        build=builds[self.player.current_choice[:-1]]((coords.x/self.cell_size,coords.y/self.cell_size),self.player.nation,self.player.current_choice)
        self.groups_manager.new_build(build)
        sprite = arcade.Sprite()
        sprite.texture = reg.images[f"resources/{build.type_data[:-1]}.png"]
        sprite.center_x = coords.x
        sprite.center_y = coords.y
        sprite.scale = 15 * self.cell_size / 128
        self.sprite_list.append(sprite)
        self.option_is_selected=False

    def update_roads(self):
        self.roads=[]
        for i in self.groups_manager.groups_set:
            print("ROAD1")
            for j in i.links_set:
                x1,y1=self.groups_manager.id_to_build[j[0]].coordinates
                x1*=self.cell_size
                y1 *= self.cell_size

                x2, y2 = self.groups_manager.id_to_build[j[1]].coordinates
                x2 *= self.cell_size
                y2 *= self.cell_size
                print((x1,y1,x2,y2))
                self.roads.append((x1,y1,x2,y2))


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
            self.fossils_view = not self.fossils_view
        elif key == arcade.key.P:
            self.create_shapes()
        elif key == arcade.key.SPACE:
            if len(self.selected_builds)==2:
                link=(self.selected_builds[0].id,self.selected_builds[1].id)
                print(link)
                self.groups_manager.new_link(link)
            elif len(self.selected_builds) > 2:
                for i in range(1, len(self.selected_builds) - 1):
                    link = (self.selected_builds[i - 1].id, self.selected_builds[i].id)
                    print(link)
                    self.groups_manager.new_link(link)
        elif key == arcade.key.ESCAPE:
            self.selected_builds=[]
            if self.show_selection_panel:
                self.show_selection_panel=False
            elif self.option_is_selected:
                self.cursor_texture = reg.images["resources/capital.png"]
                self.option_is_selected=False
            else:
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
