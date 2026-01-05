import os
import threading
import queue
import arcade


class Registry:
    def __init__(self):
        self.image_queue = queue.Queue()
        self.images = {}
        folder = os.path.join(os.path.abspath("."), "./resources")
        self.img_paths = ["resources/" + f for f in os.listdir(folder)]

    def load_image_threaded(self):
        thread = threading.Thread(
            target=self.download_image,
            args=(),
            daemon=True  # Поток завершится при закрытии приложения
        )
        thread.start()

    def download_image(self):
        try:
            for i in range(len(self.img_paths)):
                image = arcade.load_texture(self.img_paths[i])
                self.image_queue.put(('success', image,i+1,self.img_paths[i]))

        except Exception as e:
            # В случае ошибки отправляем сообщение
            self.image_queue.put(('error', str(e)))

    def check_queue(self):
        """Проверка очереди в основном потоке GUI"""
        try:
            return self.image_queue.get_nowait()
        except queue.Empty:
            return False
    

reg = Registry()
