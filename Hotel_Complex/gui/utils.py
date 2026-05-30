# gui/utils.py
import tkinter as tk
from tkinter import messagebox


def show_error(parent, message):
    """Показать окно с ошибкой."""
    messagebox.showerror("Ошибка", message, parent=parent)


def show_info(parent, message):
    """Показать информационное окно."""
    messagebox.showinfo("Информация", message, parent=parent)


def show_warning(parent, message):
    """Показать предупреждение."""
    messagebox.showwarning("Предупреждение", message, parent=parent)


def ask_yes_no(parent, question):
    """Задать вопрос Да/Нет."""
    return messagebox.askyesno("Подтверждение", question, parent=parent)


def center_window(window, width, height):
    """Центрирует окно на экране."""
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")