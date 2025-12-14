import arcade
from pyglet.graphics import Batch
from src.settings import settings
from src.registry import reg


class StartView(arcade.View):
    """Стартовый экран с таймером перехода в главное меню"""

    def __init__(self, window):
        super().__init__()
        self.window = window  # Ссылка на главное окно
        self.timer = 0.0
        self.batch = Batch()
        self.shape_list = arcade.shape_list.ShapeElementList()
        self.name_game = None
        reg.load_image_threaded(self.window.img_paths)
        self.rect_outline = None
        self.corner_text = None
        self.score = "0%"
    def setup(self):
        """Инициализация представления"""
        self.create_text()

    def on_show_view(self):
        """Вызывается при показе этого представления"""
        self.setup()
        self.timer = 0.0

    def on_draw(self):
        """Рисование"""
        self.clear()
        self.batch.draw()
        self.shape_list.draw()

    def on_update(self, delta_time):
        F = reg.check_queue()
        if F and F[0]=="success":
            self.window.images[F[-1]]=F[1]
            self.update_corner_text(f"{F[2]/len(self.window.img_paths)*100:.1f}%")
            if F[2] == len(self.window.img_paths):
                self.window.switch_view("main_menu")
        elif F and F[0]!="success":
            print(F[1])

    def on_resize(self, width: float, height: float):
        """Обработка изменения размера окна"""
        super().on_resize(width, height)
        self.create_text()
        self.update_corner_text()

    def update_corner_text(self, new_text=None):
        """Обновление текста в углу"""
        if new_text:
            self.score = new_text

        # Удаляем старый текст
        if self.corner_text:
            self.corner_text = None

        # Создаем новый
        padding_x = int(self.window.width * 0.02)
        padding_y = int(self.window.height * 0.02)
        font_size = int(self.window.height * 0.03)

        self.corner_text = arcade.Text(
            text=self.score,
            x=self.window.width-padding_x,
            y=padding_y,
            color=arcade.color.WHITE,
            font_size=font_size,
            anchor_x="center",
            anchor_y="center",
            batch=self.batch
        )

    def create_text(self):
        """Создание текста и рамки"""
        # Очищаем предыдущие объекты
        self.batch = Batch()
        if self.shape_list:
            self.shape_list.clear()

        center_x = self.window.width // 2
        center_y = self.window.height // 2

        # Расчет размера шрифта
        base_width = settings.width_min
        font_size = int(24 * (self.window.width / base_width))

        # Создаем текст
        self.name_game = arcade.Text(
            settings.title,
            center_x,
            center_y,
            arcade.color.RED,
            font_size,
            bold=True,
            align="center",
            anchor_x="center",
            anchor_y="center",
            batch=self.batch
        )

        # Создаем рамку
        text_width = self.name_game.content_width
        text_height = self.name_game.content_height
        padding = int(min(self.window.width, self.window.height) * 0.05)
        rect_width = text_width + padding
        rect_height = text_height + padding

        self.rect_outline = arcade.shape_list.create_rectangle_outline(
            center_x=center_x,
            center_y=center_y,
            width=rect_width,
            height=rect_height,
            color=arcade.color.RED,
            border_width=2
        )
        self.shape_list.append(self.rect_outline)
