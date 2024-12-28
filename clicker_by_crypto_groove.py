from mss import mss
import numpy as np
import cv2
import pyautogui
import tkinter as tk
from pynput import mouse
import threading
import time
import keyboard
import win32api, win32con
import random
from tkinter import Toplevel, Text, Scrollbar, RIGHT, Y, END


class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.roi = (0, 0, pyautogui.size().width, pyautogui.size().height)
        self.running = False
        self.point = None
        self.setup_ui()
        self.setup_hotkeys()
        self.sct = mss()  # Создаем экземпляр mss 

        # Определение цветов объектов
        self.object_colors = {
            "pink": ([147, 229, 0], [167, 255, 255]),  # розовый
            "green": ([35, 158, 83], [68, 255, 255]),  # зеленый
            "brown": ([7, 210, 69], [12, 255, 206]),  # коричневый
        }

    def setup_ui(self):
        self.root.title("Blum Auto Clicker")
        self.root.geometry("350x500")
        self.root.resizable(False, False)
        
        # Заголовок
        self.title_label = tk.Label(self.root, text="Blum Auto Clicker", font=("Helvetica", 16, "bold"), fg="#983500")
        self.title_label.pack(pady=(20, 10))

        # Общий стиль для кнопок
        button_style = {
            "font": ("Helvetica", 12), 
            "bg": "#4CAF50", 
            "fg": "white", 
            "activebackground": "#45a049",
            "relief": "raised", 
            "bd": 2, 
            "highlightthickness": 2, 
            "highlightbackground": "#3e8e41",
            "highlightcolor": "#3e8e41",
            "width": 25
        }
        
        # Кнопки управления
        self.start_button = tk.Button(self.root, text="Запустить кликер", command=self.start_clicker, **button_style)
        self.start_button.pack(pady=10, ipadx=10, ipady=5)
        
        self.stop_button = tk.Button(self.root, text="Остановить кликер", command=self.stop_clicker, state=tk.DISABLED, **button_style)
        self.stop_button.pack(pady=10, ipadx=10, ipady=5)
        
        self.setup_roi_button = tk.Button(self.root, text="Задать область кликов", command=self.setup_roi, **button_style)
        self.setup_roi_button.pack(pady=10, ipadx=10, ipady=5)
        
        self.setup_point_button = tk.Button(self.root, text="Указать кнопку старта", command=self.setup_point, **button_style)
        self.setup_point_button.pack(pady=10, ipadx=10, ipady=5)
        
        self.instructions_button = tk.Button(self.root, text="Инструкция", command=self.show_instructions, **button_style)
        self.instructions_button.pack(pady=10, ipadx=10, ipady=5)
        
        # Нижняя подпись
        self.credit_label = tk.Label(self.root, text="сделано @crypto_groove", font=("Helvetica", 10, "italic"), fg="gray")
        self.credit_label.pack(pady=20)
    
    def show_instructions(self):
        instructions = """
### 1. Запуск приложения
- Откройте приложение автокликера Blum Auto Clicker.
- Вы увидите основное окно приложения с несколькими кнопками.

### 2. Задание области кликов
- Нажмите кнопку "Задать область кликов".
- Откроется полупрозрачное синее окно.
- Используйте мышь, чтобы выделить область экрана, в которой должны происходить клики. 
  ОБЯЗАТЕЛЬНО область должна быть довольно узкой как на видео (https://t.me/crypto_groove/10)
- После выделения области окно закроется, и область будет сохранена.

### 3. Указание кнопки старта
- Нажмите кнопку "Указать кнопку старта".
- Откроется полупрозрачное красное окно.
- Кликните по кнопке в игре, на которую должен ориентироваться автокликер для начала работы.
- Окно закроется, и координаты кнопки будут сохранены.

### 4. Запуск автокликера
- Нажмите кнопку "Запустить кликер" либо сочетание клавиш ctrl+alt+s.
- Чтобы приостановить или возобновить работу автокликера, используйте комбинацию клавиш Ctrl+Alt+S.

Спасибо за покупку от https://t.me/crypto_groove
⊂(◉‿◉)つ
"""
        instruction_window = Toplevel(self.root)
        instruction_window.title("Инструкция")
        instruction_window.geometry("400x400")

        text_widget = Text(instruction_window, wrap='word', font=("Helvetica", 10))
        text_widget.insert(END, instructions)
        text_widget.tag_add("important", "10.0", "10.93")  # Adjust the range to cover the important text
        text_widget.tag_config("important", foreground="red")
        text_widget.config(state='disabled')
        text_widget.pack(side="left", fill="both", expand=True)

        scrollbar = Scrollbar(instruction_window, command=text_widget.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        text_widget.config(yscrollcommand=scrollbar.set)

    def setup_hotkeys(self):
        keyboard.add_hotkey('ctrl+alt+s', self.toggle_clicker)
    
    def toggle_clicker(self):
        if self.running:
            self.stop_clicker()
        else:
            self.start_clicker()

    def setup_roi(self):
        threading.Thread(target=self.select_roi, daemon=True).start()

    def select_roi(self):
        self.roi_window = tk.Toplevel(self.root)
        self.roi_window.overrideredirect(1)
        self.roi_window.attributes('-alpha', 0.3)
        self.roi_window['bg'] = 'blue'
        self.roi_window.geometry(f"{pyautogui.size().width}x{pyautogui.size().height}+0+0")

        self.start_x = None
        self.start_y = None

        def on_click(x, y, button, pressed):
            if pressed:
                self.start_x, self.start_y = x, y
            else:
                if self.start_x is not None and self.start_y is not None:
                    roi_width = abs(x - self.start_x)
                    roi_height = abs(y - self.start_y)
                    self.roi = (min(self.start_x, x), min(self.start_y, y), roi_width, roi_height)
                    self.roi_window.destroy()
                    print(f"ROI set to: {self.roi}")
                    return False  # Остановить прослушивание

        def on_move(x, y):
            if self.start_x is not None and self.start_y is not None:
                self.roi_window.geometry(f'{abs(x - self.start_x)}x{abs(y - self.start_y)}+{min(x, self.start_x)}+{min(y, self.start_y)}')

        # Подключение слушателей мыши
        listener = mouse.Listener(on_click=on_click, on_move=on_move)
        listener.start()
        listener.join()

    def setup_point(self):
        threading.Thread(target=self.select_point, daemon=True).start()

    def select_point(self):
        self.point_window = tk.Toplevel(self.root)
        self.point_window.overrideredirect(1)
        self.point_window.attributes('-alpha', 0.3)
        self.point_window['bg'] = 'red'
        self.point_window.geometry(f"{pyautogui.size().width}x{pyautogui.size().height}+0+0")

        def on_click(x, y, button, pressed):
            if pressed:
                self.point = (x, y)
                self.point_window.destroy()
                print(f"Point set to: {self.point}")
                return False  # Остановить прослушивание

        # Подключение слушателей мыши
        listener = mouse.Listener(on_click=on_click)
        listener.start()
        listener.join()

    def start_clicker(self):
        self.running = True
        threading.Thread(target=self.run_clicker, daemon=True).start()
        threading.Thread(target=self.periodic_check, daemon=True).start()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_clicker(self):
        self.running = False
        cv2.destroyAllWindows()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def run_clicker(self):
        while self.running:
            self.capture_and_process()

    def capture_and_process(self):
        with mss() as sct:
            while self.running:
                monitor = {"top": self.roi[1], "left": self.roi[0], "width": self.roi[2], "height": self.roi[3]}
                sct_img = sct.grab(monitor)
                frame = np.array(sct_img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                for object_name, (lower_color, upper_color) in self.object_colors.items():
                    mask = cv2.inRange(hsv, np.array(lower_color), np.array(upper_color))
                    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                    for contour in contours:
                        M = cv2.moments(contour)
                        if M['m00'] != 0:
                            cx = int(M['m10'] / M['m00']) + self.roi[0]
                            cy = int(M['m01'] / M['m00']) + self.roi[1]
                            self.click_mouse(cx, cy + 10) #смещение
                            time.sleep(random.uniform(0.005, 0.015))

    def periodic_check(self):
        check_interval = 3  # Проверка каждую секунду
        while self.running:
            if self.point:
                self.check_and_click_point()
            time.sleep(check_interval)

    def check_and_click_point(self):
        if not self.point:
            return
        x, y = self.point
        color = pyautogui.screenshot().getpixel((x, y))
        if color == (255, 255, 255):  # Проверка на белый цвет
            print(f"Clicking at {self.point}")
            self.click_mouse(x, y)

    def click_mouse(self, x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()
