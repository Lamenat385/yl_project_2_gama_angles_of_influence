import arcade
import arcade.gui
import random
from typing import List
from arcade.particles import FadeParticle, Emitter, EmitBurst, EmitInterval, EmitMaintainCount
from src.registry import reg


class MainMenuView(arcade.View):
    """Главное меню игры с падающими спрайтами и физикой"""

    def __init__(self, window):
        super().__init__()
        self.window = window
        self.manager = None

        # Списки для физики
        self.falling_sprites = arcade.SpriteList()  # Падающие объекты
        self.platform_sprites = arcade.SpriteList()  # Платформы для коллизий
        self.emitters = []  # Добавлено: список эмиттеров частиц

        # Таймер спавна
        self.time_since_last_spawn = 0.0
        self.spawn_interval = 1.0  # Спавн каждую секунду

        # Флаг для отложенного создания платформ под кнопками
        self.platforms_created = False
        self.button_widgets = []  # Сохраняем ссылки на кнопки

    def on_show_view(self):
        """Вызывается при показе представления"""
        # Сброс состояния
        self.falling_sprites = arcade.SpriteList()
        self.platform_sprites = arcade.SpriteList()
        self.emitters.clear()  # Добавлено: очистка эмиттеров
        self.time_since_last_spawn = 0.0
        self.platforms_created = False
        self.button_widgets = []

        self.create_ui()

        # Создаем базовые платформы (границы экрана)
        self._create_boundary_platforms()

    def _create_boundary_platforms(self):
        """Создаем невидимые платформы по границам экрана"""
        # Нижняя граница (толстая для надежной коллизии)
        bottom = arcade.SpriteSolidColor(int(self.window.width), 10, arcade.color.TRANSPARENT_BLACK)
        bottom.center_x = self.window.width / 2
        bottom.center_y = 5
        self.platform_sprites.append(bottom)

        # Боковые границы
        left = arcade.SpriteSolidColor(10, int(self.window.height), arcade.color.TRANSPARENT_BLACK)
        left.center_x = 5
        left.center_y = self.window.height / 2
        self.platform_sprites.append(left)

        right = arcade.SpriteSolidColor(10, int(self.window.height), arcade.color.TRANSPARENT_BLACK)
        right.center_x = self.window.width - 5
        right.center_y = self.window.height / 2
        self.platform_sprites.append(right)

    def on_draw(self):
        """Рисование"""
        self.clear((30, 30, 40))  # Темный фон для контраста

        # Рисуем платформы (временно для отладки - закомментируйте для прозрачности)
        # self.platform_sprites.draw()

        # Рисуем падающие спрайты
        self.falling_sprites.draw()

        # Добавлено: рисуем частицы
        for emitter in self.emitters:
            emitter.draw()

        # Рисуем интерфейс
        if self.manager:
            self.manager.draw()

        # Отладочная информация
        arcade.draw_text(
            f"Падающих объектов: {len(self.falling_sprites)}",
            10, self.window.height - 30,
            arcade.color.GRAY, 14
        )

    def on_update(self, delta_time: float):
        """Обновление физики и спавн объектов"""
        # Спавн новых спрайтов
        self.time_since_last_spawn += delta_time
        if self.time_since_last_spawn >= self.spawn_interval:
            self._spawn_falling_sprite()
            self.time_since_last_spawn = 0

        # Обновляем позиции спрайтов вручную (без PhysicsEnginePlatformer для простоты и контроля скорости)
        for sprite in self.falling_sprites:
            sprite.change_y -= 400 * delta_time  # Гравитация

            # Ограничение максимальной скорости падения
            if sprite.change_y < -300:
                sprite.change_y = -300

            sprite.center_y += sprite.change_y * delta_time
            sprite.center_x += sprite.change_x * delta_time

            # === ЗАМЕНИТЕ ЭТОТ БЛОК ===
            hit_list = arcade.check_for_collision_with_list(sprite, self.platform_sprites)
            if hit_list:
                self._create_particles(sprite.center_x, sprite.center_y - sprite.height / 2)
                sprite.remove_from_sprite_lists()
                continue
            # === КОНЕЦ ЗАМЕНЫ ===аем горизонтальное движение

        # Добавлено: обновляем и удаляем старые эмиттеры
        for emitter in self.emitters[:]:
            emitter.update()
            if emitter.can_reap():  # Эмиттер закончил работу и все частицы исчезли
                self.emitters.remove(emitter)

                # Создаем платформы под кнопками после их расположения (после первого кадра)
        if not self.platforms_created and self.manager and self.button_widgets:
            # Проверяем, что кнопки имеют корректные координаты (после первого кадра)
            if all(button.center_x != 0 and button.center_y != 0 for button in self.button_widgets):
                self._create_button_platforms()
                self.platforms_created = True

    # Добавлено: метод создания частиц
    def _create_particles(self, x, y):
        """Создаем простые белые частицы при коллизии"""
        # Создаем текстуру частицы один раз (можно вынести в __init__ для оптимизации)
        particle_texture = arcade.make_soft_circle_texture(30, arcade.color.RED, 180, 6)

        emitter = Emitter(
            center_xy=(x, y),
            emit_controller=EmitBurst(40),
            particle_factory=lambda e: FadeParticle(
                filename_or_texture=particle_texture,
                change_xy=arcade.math.rand_in_circle((0.0, 0.0), 1.0),
                lifetime=random.uniform(0.5, 1.1),
                start_alpha=255, end_alpha=0,
                scale=random.uniform(0.35, 0.6),
            ),
        )

        self.emitters.append(emitter)

    def _create_button_platforms(self):
        """Создаем невидимые платформы под кнопками на основе их реальных позиций"""
        # Удаляем старые платформы кнопок (оставляем только границы)
        # Идентифицируем границы по размеру и позиции
        for sprite in self.platform_sprites[:]:
            # Пропускаем границы (они имеют большой размер или находятся у краев)
            if (sprite.width > 100 or sprite.height > 100 or
                    sprite.center_y < 20 or sprite.center_x < 20 or sprite.center_x > self.window.width - 20):
                continue
            sprite.remove_from_sprite_lists()

        # Создаем платформы под кнопками
        for button in self.button_widgets:
            try:
                # В новых версиях arcade SpriteSolidColor принимает только ширину, высоту и цвет
                platform = arcade.SpriteSolidColor(
                    int(button.width),
                    int(button.height),
                    arcade.color.TRANSPARENT_BLACK
                )
                platform.center_x = button.center_x
                platform.center_y = button.center_y

                self.platform_sprites.append(platform)
            except Exception as e:
                print(f"Ошибка создания платформы для кнопки: {e}")

    def _spawn_falling_sprite(self):
        """Создаем новый падающий спрайт с разнообразием"""
        # Случайный выбор спрайта из ресурсов

        sprite = arcade.Sprite(reg.images["resources/fall_zombie.png"], 0.5)
        sprite.center_x = random.randint(50, self.window.width - 50)
        sprite.center_y = self.window.height + 30  # Начинаем за верхней границей

        # Добавляем небольшое горизонтальное смещение для разнообразия
        sprite.change_x = random.uniform(-50, 50)

        # Начальная скорость = 0 (будет нарастать под действием гравитации)
        sprite.change_y = 0

        # Добавляем в список
        self.falling_sprites.append(sprite)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.switch_view("start")

    def create_ui(self):
        """Создание интерфейса главного меню"""
        # Очищаем предыдущий менеджер
        if self.manager:
            self.manager.clear()
            self.manager.disable()

        # Создаем новый менеджер GUI
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Создаем контейнер с якорями (anchor layout)
        anchor_layout = arcade.gui.UIAnchorLayout()

        # Создаем вертикальный контейнер для элементов
        v_box = arcade.gui.UIBoxLayout(vertical=True)

        # Заголовок
        title = arcade.gui.UILabel(
            text="Главное меню",
            font_size=32,
            font_name=("Arial", "Calibri", "sans-serif"),
            text_color=arcade.color.GOLD,
            bold=True,
            width=300,
            align="center"
        )
        v_box.add(title)

        # Отступ после заголовка
        v_box.add(arcade.gui.UIBoxLayout(height=40))

        # Кнопки
        buttons_data = [
            ("Начать игру", "stuart_game"),
            ("Настройки", "settings"),
            ("Выход", "exit")
        ]

        for text, view_name in buttons_data:
            button = create_button(text)
            self.button_widgets.append(button)  # Сохраняем для создания платформ

            # Создаем замыкание для каждой кнопки
            def create_handler(name):
                return lambda event: self.window.switch_view(name)

            button.on_click = create_handler(view_name)
            v_box.add(button)
            v_box.add(arcade.gui.UIBoxLayout(height=15))  # Больше отступ между кнопками

        # Добавляем вертикальный контейнер в anchor layout
        anchor_layout.add(
            child=v_box,
            anchor_x="center_x",
            anchor_y="center_y"
        )

        # Добавляем anchor layout в менеджер
        self.manager.add(anchor_layout)

    def on_hide_view(self):
        """Вызывается при скрытии представления"""
        if self.manager:
            self.manager.disable()
        # Очищаем спрайты при уходе из меню
        self.falling_sprites.clear()
        self.platform_sprites.clear()
        # Добавлено: очистка частиц
        for emitter in self.emitters:
            self.emitters.remove(emitter)
        self.emitters.clear()

    def on_resize(self, width: float, height: float):
        """Обработка изменения размера окна"""
        super().on_resize(width, height)
        # Пересоздаем интерфейс и платформы
        self.create_ui()
        self._create_boundary_platforms()
        self.platforms_created = False  # Сбрасываем флаг для пересоздания платформ кнопок


def create_button(text, color_scheme="blue"):
    color_map = {
        "blue": {"normal": (57, 91, 158), "hover": (72, 118, 205), "press": (35, 60, 110)},
        "green": {"normal": (57, 158, 91), "hover": (72, 205, 118), "press": (35, 110, 60)},
        "red": {"normal": (158, 57, 57), "hover": (205, 72, 72), "press": (110, 35, 35)}
    }

    colors = color_map[color_scheme]

    return arcade.gui.UIFlatButton(
        text=text,
        width=240,  # Чуть шире для лучшей коллизии
        height=60,  # Чуть выше
        style={
            "normal": {
                "font_name": "Arial",
                "font_size": 20,
                "font_color": arcade.color.WHITE,
                "bg_color": colors["normal"],
                "border_color": arcade.color.WHITE,
                "border_width": 2
            },
            "hover": {
                "bg_color": colors["hover"],
                "border_color": (255, 215, 0),
                "border_width": 3
            },
            "press": {
                "bg_color": colors["press"],
                "font_color": arcade.color.YELLOW,
                "border_width": 3
            }
        }
    )
