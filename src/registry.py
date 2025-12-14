import threading
import queue
import arcade


class Registry:
    def __init__(self):
        self.image_queue = queue.Queue()

    def load_image_threaded(self,names):
        thread = threading.Thread(
            target=self.download_image,
            args=(names,),
            daemon=True  # Поток завершится при закрытии приложения
        )
        thread.start()

    def download_image(self, names):
        try:
            for i in range(len(names)):
                image = arcade.load_texture(names[i])
                self.image_queue.put(('success', image,i+1,names[i]))

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
