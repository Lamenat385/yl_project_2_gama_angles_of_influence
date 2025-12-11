import arcade
import arcade.gui


class MainMenuView(arcade.View):
    """Главное меню игры"""

    def __init__(self, window):
        super().__init__()
        self.window = window
        self.manager = None
        # Не создаем UI здесь, ждем on_show_view

    def on_show_view(self):
        """Вызывается при показе этого представления"""
        self.create_ui()

    def on_draw(self):
        """Рисование"""
        self.clear()
        if self.manager:
            self.manager.draw()

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
            text_color=arcade.color.RED,
            bold=True,
            width=300,
            align="center"
        )
        v_box.add(title)

        # Отступ после заголовка
        v_box.add(arcade.gui.UIBoxLayout(height=40))

        # Кнопки
        buttons_data = [
            ("Начать игру", "start_game"),
            ("Настройки", "settings"),
            ("Выход", "exit")
        ]

        for text, view_name in buttons_data:
            button = arcade.gui.UIFlatButton(
                text=text,
                width=200,
                height=40
            )

            # Создаем замыкание для каждой кнопки
            def create_handler(name):
                return lambda event: self.window.switch_view(name)

            button.on_click = create_handler(view_name)
            v_box.add(button)
            v_box.add(arcade.gui.UIBoxLayout(height=10))

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

    def on_resize(self, width: float, height: float):
        """Обработка изменения размера окна"""
        super().on_resize(width, height)
        self.create_ui()