import arcade
import arcade.gui


class SettingsView(arcade.View):
    """Экран настроек с регулировкой громкости"""

    def __init__(self, window):
        super().__init__()
        self.window = window
        self.manager = None
        self.volume_slider = None
        self.volume_label = None
        self.music_player = None  # Ссылка на плеер музыки

    def on_show_view(self):
        """Инициализация при показе экрана настроек"""
        # Пытаемся получить плеер музыки из окна (если он там хранится)
        self.create_ui()
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        """Отрисовка интерфейса"""
        self.clear()
        if self.manager:
            self.manager.draw()

    def on_key_press(self, key, modifiers):
        """Обработка нажатия ESC для возврата в главное меню"""
        if key == arcade.key.ESCAPE:
            self.window.switch_view("main_menu")

    def create_ui(self):
        """Создание интерфейса настроек громкости"""
        # Очищаем предыдущий менеджер
        if self.manager:
            self.manager.clear()
            self.manager.disable()

        # Создаем новый менеджер GUI
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Основной контейнер
        anchor_layout = arcade.gui.UIAnchorLayout()

        # Вертикальный контейнер для элементов
        v_box = arcade.gui.UIBoxLayout(vertical=True, space_between=20)

        # Заголовок "Громкость"
        title = arcade.gui.UILabel(
            text="Громкость",
            font_size=36,
            font_name=("Arial", "Calibri", "sans-serif"),
            text_color=arcade.color.WHITE,
            bold=True,
            width=400,
            align="center"
        )
        v_box.add(title)

        # Текущее значение громкости (динамически обновляется)
        self.volume_label = arcade.gui.UILabel(
            text="50%",
            font_size=24,
            font_name=("Arial", "Calibri", "sans-serif"),
            text_color=arcade.color.LIGHT_GRAY,
            width=400,
            align="center"
        )
        v_box.add(self.volume_label)

        # Ползунок громкости
        current_volume = 0.5  # Значение по умолчанию
        if self.music_player and hasattr(self.music_player, 'volume'):
            current_volume = self.music_player.volume

        self.volume_slider = arcade.gui.UISlider(
            value=current_volume * 100,  # UISlider работает в диапазоне 0-100
            width=300,
            height=30
        )
        v_box.add(self.volume_slider)

        # Обработчик изменения значения ползунка
        @self.volume_slider.event("on_change")
        def on_volume_change(event):
            volume_percent = int(event.new_value)
            volume_float = event.new_value / 100.0
            self.volume_label.text = f"{volume_percent}%"

            # Применяем громкость к музыке
            if self.window.music_player:
                self.window.music_player.volume = volume_float

        # Отступ
        v_box.add(arcade.gui.UIBoxLayout(height=30))

        # Кнопка "Назад"
        back_button = arcade.gui.UIFlatButton(
            text="← Назад",
            width=180,
            height=50,
            style={
                "normal": {
                    "font_name": "Arial",
                    "font_size": 18,
                    "font_color": arcade.color.WHITE,
                    "bg_color": (70, 70, 70),
                    "border_color": arcade.color.WHITE,
                    "border_width": 2
                },
                "hover": {
                    "bg_color": (90, 90, 90),
                    "border_color": arcade.color.GOLD
                },
                "press": {
                    "bg_color": (50, 50, 50),
                    "font_color": arcade.color.GOLD
                }
            }
        )

        @back_button.event("on_click")
        def on_back_click(event):
            self.window.switch_view("main_menu")

        v_box.add(back_button)

        # Центрируем контейнер
        anchor_layout.add(
            child=v_box,
            anchor_x="center_x",
            anchor_y="center_y"
        )

        self.manager.add(anchor_layout)

    def on_hide_view(self):
        """Очистка при скрытии экрана"""
        if self.manager:
            self.manager.disable()

    def on_resize(self, width: float, height: float):
        """Пересоздание интерфейса при изменении размера окна"""
        super().on_resize(width, height)
        self.create_ui()