from PIL import Image, ImageTk, ImageSequence
import tkinter as tk

class AnimatedGIF(tk.Label):
    def __init__(self, master, path, delay=35):
        # Открываем GIF файл и загружаем все его кадры
        im = Image.open(path)
        new_size = (60, 60)
        self.resize = [frame.copy().resize(new_size, Image.BILINEAR) for frame in ImageSequence.Iterator(im)]
        self.frames = [ImageTk.PhotoImage(frame.copy().convert("RGBA")) for frame in self.resize]
        self.delay = delay  # задержка между кадрами (в миллисекундах)
        self.frame_idx = 0 

        self.label = tk.Label(master, bg="#2e3f4f")  # Отображение анимации
        self.label.pack(side="right")  # Размещаем GIF по правому краю и добавляем отступы

        self.update_animation()  # запуск анимации

    def update_animation(self):
        # Обновление анимации
        self.label.config(image=self.frames[self.frame_idx])
        self.frame_idx = (self.frame_idx + 1) % len(self.frames)  # Переход к следующему кадру
        self.label.after(self.delay, self.update_animation)  # Устанавливает таймер для обновления анимации

    def stop(self):
        self.label.destroy()