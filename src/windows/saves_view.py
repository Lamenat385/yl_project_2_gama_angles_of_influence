import arcade
import arcade.gui
import csv
import os
from pathlib import Path


class SaveGameView(arcade.View):
    """Окно сохранений игр"""

    def __init__(self, window):
        super().__init__()
        self.window = window
        self.manager = None
        self.saves_data = []
        self.scroll_area = None
        self.current_scroll = 0

    def on_show_view(self):
        """Вызывается при показе этого представления"""
        self.load_saves_data()
        self.create_ui()

    def on_draw(self):
        """Рисование"""
        self.clear()
        if self.manager:
            self.manager.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.switch_view("main_menu")

    def load_saves_data(self):
        """Загрузка данных сохранений из CSV файла"""
        self.saves_data = []

        # Проверяем существование файла
        csv_path = Path("data/saves.csv")
        if not csv_path.exists():
            print("Файл saves.csv не найден")
            return

        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=";")
                for row in reader:
                    # Проверяем существование файла изображения
                    img_path = row.get('image_path', '')
                    if img_path and not Path(img_path).exists():
                        print(f"Изображение не найдено: {img_path}")
                        img_path = None

                    save_item = {
                        'image_path': img_path,
                        'name': row.get('name', 'Без названия'),
                        'time': row.get('time', '0:00')
                    }
                    self.saves_data.append(save_item)
        except Exception as e:
            print(f"Ошибка загрузки CSV: {e}")

    def create_ui(self):
        """Создание интерфейса окна сохранений"""
        # Очищаем предыдущий менеджер
        if self.manager:
            self.manager.clear()
            self.manager.disable()

        # Создаем новый менеджер GUI
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Создаем основной вертикальный контейнер
        main_layout = arcade.gui.UIBoxLayout(vertical=True)

        # Верхняя панель с заголовком и кнопкой
        top_panel = arcade.gui.UIBoxLayout(vertical=False)

        # Заголовок с левым отступом
        title_container = arcade.gui.UIBoxLayout(vertical=False)
        title_container.add(arcade.gui.UIBoxLayout(width=20))  # Левый отступ

        title = arcade.gui.UILabel(
            text="Сохранения",
            font_size=32,
            font_name=("Arial", "Calibri", "sans-serif"),
            text_color=arcade.color.WHITE,
            bold=True,
            width=400,
            align="left"
        )
        title_container.add(title)
        top_panel.add(title_container)

        # Гибкое пространство между заголовком и кнопкой
        top_panel.add(arcade.gui.UIBoxLayout(width=100, height=0))

        # Кнопка "Создать новую игру"
        new_game_button = create_button("Создать новую игру", color_scheme="green")
        new_game_button.on_click = self.on_new_game_click

        # Контейнер для кнопки с правым отступом
        button_container = arcade.gui.UIBoxLayout(vertical=False)
        button_container.add(new_game_button)
        button_container.add(arcade.gui.UIBoxLayout(width=20))  # Правый отступ
        top_panel.add(button_container)

        # Добавляем верхнюю панель с вертикальными отступами
        main_layout.add(arcade.gui.UIBoxLayout(height=20))  # Верхний отступ
        main_layout.add(top_panel)
        main_layout.add(arcade.gui.UIBoxLayout(height=40))  # Больший отступ, так как линия рисуется отдельно

        # Вертикальный список сохранений
        saves_list = arcade.gui.UIBoxLayout(vertical=True)

        if not self.saves_data:
            # Если нет сохранений, показываем сообщение
            empty_label = arcade.gui.UILabel(
                text="Нет сохранений",
                font_size=24,
                font_name=("Arial", "Calibri", "sans-serif"),
                text_color=arcade.color.GRAY,
                align="center",
                width=self.window.width - 40
            )
            empty_container = arcade.gui.UIBoxLayout(vertical=False)
            empty_container.add(arcade.gui.UIBoxLayout(width=20))
            empty_container.add(empty_label)
            empty_container.add(arcade.gui.UIBoxLayout(width=20))
            saves_list.add(empty_container)
        else:
            # Ограничиваем количество отображаемых сохранений
            max_saves = min(len(self.saves_data), 5)

            # Создаем элементы списка для каждого сохранения
            for i in range(max_saves):
                save = self.saves_data[i]
                save_item = self.create_save_item(save, i)
                saves_list.add(save_item)

            # Если сохранений больше, чем можем показать
            if len(self.saves_data) > max_saves:
                more_label = arcade.gui.UILabel(
                    text=f"... и ещё {len(self.saves_data) - max_saves} сохранений",
                    font_size=18,
                    font_name=("Arial", "Calibri", "sans-serif"),
                    text_color=arcade.color.LIGHT_GRAY,
                    align="center",
                    width=self.window.width - 40
                )
                more_container = arcade.gui.UIBoxLayout(vertical=False)
                more_container.add(arcade.gui.UIBoxLayout(width=20))
                more_container.add(more_label)
                more_container.add(arcade.gui.UIBoxLayout(width=20))
                saves_list.add(more_container)

        main_layout.add(saves_list)

        # Добавляем основной контейнер в окно
        self.manager.add(main_layout)

    def create_save_item(self, save_data, index):
        """Создание элемента списка сохранения"""
        # Основной контейнер элемента с фиксированной высотой
        item_height = 100
        item_container = arcade.gui.UIBoxLayout(vertical=False)

        # Размер картинки (10% от ширины окна)
        image_size = int(self.window.width * 0.1)

        # Загружаем текстуру изображения или создаем заглушку
        texture = None
        if save_data['image_path'] and os.path.exists(save_data['image_path']):
            try:
                texture = arcade.load_texture(save_data['image_path'])
            except:
                texture = self.create_placeholder_texture(image_size)
        else:
            texture = self.create_placeholder_texture(image_size)

        # Создаем виджет картинки
        image_widget = arcade.gui.UITextureButton(
            texture=texture,
            width=image_size,
            height=image_size
        )
        image_widget.on_click = lambda event, idx=index: self.on_save_clicked(idx)

        # Контейнер для текста
        text_layout = arcade.gui.UIBoxLayout(vertical=True)

        # Название сохранения
        name_label = arcade.gui.UILabel(
            text=save_data['name'],
            font_size=24,
            font_name=("Arial", "Calibri", "sans-serif"),
            text_color=arcade.color.WHITE,
            align="left",
            width=self.window.width - image_size - 80
        )

        # Проведенное время
        time_label = arcade.gui.UILabel(
            text=f"Время: {save_data['time']}",
            font_size=18,
            font_name=("Arial", "Calibri", "sans-serif"),
            text_color=arcade.color.LIGHT_GRAY,
            align="left",
            width=self.window.width - image_size - 80
        )

        text_layout.add(name_label)
        text_layout.add(time_label)

        # Контейнер для текста с отступом от картинки
        text_container = arcade.gui.UIBoxLayout(vertical=False)
        text_container.add(arcade.gui.UIBoxLayout(width=20))  # Отступ между картинкой и текстом
        text_container.add(text_layout)

        # Добавляем элементы в основной контейнер
        item_container.add(image_widget)
        item_container.add(text_container)

        # Простая кнопка без сложного стиля для кликабельной области
        clickable_button = arcade.gui.UIFlatButton(
            text="",
            width=self.window.width - 40,
            height=item_height
        )

        # Назначаем обработчик клика
        clickable_button.on_click = lambda event, idx=index: self.on_save_clicked(idx)

        # Контейнер с отступами по бокам
        final_container = arcade.gui.UIBoxLayout(vertical=False)
        final_container.add(arcade.gui.UIBoxLayout(width=20))  # Левый отступ

        # Просто добавляем кнопку (без сложной структуры с наложением)
        button_container = arcade.gui.UIBoxLayout(vertical=False)
        button_container.add(clickable_button)
        final_container.add(button_container)

        final_container.add(arcade.gui.UIBoxLayout(width=20))  # Правый отступ

        # Добавляем вертикальные отступы между элементами
        full_container = arcade.gui.UIBoxLayout(vertical=True)
        full_container.add(arcade.gui.UIBoxLayout(height=10))  # Верхний отступ
        full_container.add(final_container)
        full_container.add(arcade.gui.UIBoxLayout(height=10))  # Нижний отступ

        return full_container

    def create_placeholder_texture(self, size):
        """Создание текстуры-заглушки"""
        # Создаем простую текстуру для заглушки
        return arcade.Texture.create_empty(f"placeholder_{size}", (size, size))

    def on_save_clicked(self, save_index):
        """Обработчик клика на сохранение"""
        if 0 <= save_index < len(self.saves_data):
            save = self.saves_data[save_index]
            print(f"Выбрано сохранение: {save['name']} (время: {save['time']})")
            # Здесь можно добавить логику загрузки сохранения

    def on_new_game_click(self, event):
        """Обработчик клика на кнопку создания новой игры"""
        print("Создание новой игры...")
        # Здесь можно перейти к созданию новой игры

    def on_hide_view(self):
        """Вызывается при скрытии представления"""
        if self.manager:
            self.manager.disable()

    def on_resize(self, width: float, height: float):
        """Обработка изменения размера окна"""
        super().on_resize(width, height)
        self.create_ui()


def create_button(text, color_scheme="blue"):
    color_map = {
        "blue": {"normal": (57, 91, 158), "hover": (72, 118, 205), "press": (35, 60, 110)},
        "green": {"normal": (57, 158, 91), "hover": (72, 205, 118), "press": (35, 110, 60)},
        "red": {"normal": (158, 57, 57), "hover": (205, 72, 72), "press": (110, 35, 35)}
    }

    colors = color_map[color_scheme]

    return arcade.gui.UIFlatButton(
        text=text,
        width=220,
        height=55,
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
                "border_color": (255, 215, 0)
            },
            "press": {
                "bg_color": colors["press"],
                "font_color": arcade.color.YELLOW
            }
        }
    )
