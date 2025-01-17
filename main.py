import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yt_dlp
import threading
import os
import time

# Глобальные переменные
folder = None  # Папка сохранения
is_downloading = False  # Флаг для отслеживания процесса загрузки
stop_flag = False  # Флаг для остановки загрузки



# Создание основного окна
root = tk.Tk()
root.title("Скачивание видео")
root.geometry("500x400")

# Контекстное меню
context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label="Вставить", command=lambda: root.focus_get().event_generate('<<Paste>>'))

def show_context_menu(event):
    widget = event.widget
    if isinstance(widget, (tk.Entry, tk.Text)):
        context_menu.post(event.x_root, event.y_root)

root.bind("<Button-3>", show_context_menu)  # ПКМ для вызова меню

# Виджеты
url_label = tk.Label(root, text="Введите URL видео:")
url_label.pack(pady=5)

url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

# Прогресс-бар
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)

# Текст прогресса
progress_label = tk.Label(root, text="Загружено: 0%")
progress_label.pack(pady=5)

# Кнопка для скачивания
download_button = tk.Button(root, text="Скачать видео", command=lambda: start_download(), relief="flat")
download_button.pack(pady=5)

# Кнопка для остановки загрузки
stop_button = tk.Button(root, text="Стоп", command=lambda: stop_download(), relief="flat", state="disabled")
stop_button.pack(pady=5)

# Кнопка выбора папки для сохранения видео
choose_folder_button = tk.Button(root, text="Выбрать папку", command=lambda: choose_folder())
choose_folder_button.pack(pady=5)

# Отображение пути к папке
folder_label = tk.Label(root, text="Папка сохранения: не выбрана")
folder_label.pack(pady=5)

# Функция для выбора папки для сохранения
def choose_folder():
    global folder
    folder = filedialog.askdirectory()
    if folder:
        folder_label.config(text=f"Папка сохранения: {folder}")

# Функция для скачивания видео
def start_download():
    global is_downloading, stop_flag
    if is_downloading:
        messagebox.showwarning("Загрузка", "Видео уже загружается!")
        return

    url = url_entry.get()
    if not url:
        messagebox.showwarning("Ошибка", "Введите URL видео!")
        return
    if not folder:
        messagebox.showwarning("Ошибка", "Выберите папку для сохранения!")
        return

    def run_download():
        global is_downloading, stop_flag
        is_downloading = True
        stop_flag = False  # Сброс флага остановки
        stop_button.config(state="normal")

        ydl_opts = {
            'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),  # Путь для сохранения
            'format': 'best',
            'progress_hooks': [progress_hook],  # Хук для прогресса
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                if not stop_flag:
                    messagebox.showinfo("Успех", "Видео скачано успешно!")
        except Exception as e:
            if not stop_flag:
                messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
        finally:
            is_downloading = False
            stop_button.config(state="disabled")
            progress_label.config(text="Загружено: 0%")
            progress_bar['value'] = 0

    # Запуск скачивания в отдельном потоке
    download_thread = threading.Thread(target=run_download, daemon=True)
    download_thread.start()

# Функция для обновления прогресса скачивания
def progress_hook(d):
    global stop_flag
    if stop_flag:
        raise yt_dlp.utils.DownloadError("Загрузка остановлена пользователем.")
    
    if d['status'] == 'downloading':
        downloaded_bytes = d.get('downloaded_bytes', 0)
        total_bytes = d.get('total_bytes', 1)

        percent = (downloaded_bytes / total_bytes) * 100
        progress_bar['value'] = percent
        progress_label.config(text=f"Загружено: {int(percent)}%")
        root.update_idletasks()

# Функция для остановки загрузки
def stop_download():
    global stop_flag
    if is_downloading:
        stop_flag = True
        messagebox.showinfo("Остановка", "Загрузка остановлена.")
    else:
        messagebox.showwarning("Ошибка", "Нет активной загрузки!")

# Запуск основного интерфейса
root.mainloop()
