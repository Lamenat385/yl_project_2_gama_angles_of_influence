import arcade
from src.settings import settings


class BaseWindow(arcade.Window):
    """Базовое окно для всех окон игры"""

    def __init__(self):
        super().__init__(settings.width, settings.height, settings.title,
                         resizable=settings.resizable, fullscreen=settings.fullscreen)
        self.set_minimum_size(settings.width_min, settings.height_min)
        self.center_window()
        self.background_color = arcade.color.BLACK
        self.set_fullscreen(not self.fullscreen)
        # Храним представления
        self.views = {}

    def get_view(self, view_name):
        """Получить или создать представление по имени"""
        if view_name not in self.views:
            self.set_mouse_visible(True)
            if view_name == "start":
                from src.windows.start_view import StartView
                self.views[view_name] = StartView(self)
            elif view_name == "main_menu":
                from src.windows.main_menu_view import MainMenuView
                self.views[view_name] = MainMenuView(self)
            elif view_name == "start_game":
                from src.windows.saves_view import SaveGameView
                self.views[view_name] = SaveGameView(self)
            elif view_name == "stuart_game":
                from src.windows.game_view import GameView
                self.views[view_name] = GameView(self)

        return self.views[view_name]

    def switch_view(self, view_name):
        if view_name != "exit":
            view = self.get_view(view_name)
            self.show_view(view)
        else:
            arcade.exit()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.Q:
            self.close()
