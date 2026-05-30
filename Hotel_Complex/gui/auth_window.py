# gui/auth_window.py
import tkinter as tk
from tkinter import ttk
from gui.sizes import AUTH_WINDOW
from gui.utils import center_window


class AuthWindow:
    """Окно авторизации (выбор роли)."""

    def __init__(self, on_login_success):
        self.on_login_success = on_login_success
        self.window = tk.Tk()
        self.window.title("Авторизация - Гостиничный комплекс")
        self.window.resizable(False, False)


        width = AUTH_WINDOW['width']
        height = AUTH_WINDOW['height']
        self.window.geometry(f"{width}x{height}")
        center_window(self.window, width, height)

        self._create_widgets()

    def _create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="40")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = tk.Label(main_frame, text="Гостиничный комплекс",
                               font=('Arial', 22, 'bold'))
        title_label.pack(pady=(0, 30))

        subtitle_label = tk.Label(main_frame, text="Система управления",
                                  font=('Arial', 14))
        subtitle_label.pack(pady=(0, 40))

        role_frame = ttk.LabelFrame(main_frame, text="Выберите роль пользователя", padding="20")
        role_frame.pack(fill=tk.X, pady=(0, 40))

        self.role_var = tk.StringVar(value='manager')

        ttk.Radiobutton(role_frame, text="Менеджер", variable=self.role_var,
                        value='manager').pack(anchor='w', pady=10)
        ttk.Radiobutton(role_frame, text="Администратор", variable=self.role_var,
                        value='admin').pack(anchor='w', pady=10)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 20))

        login_btn = ttk.Button(button_frame, text="Войти в систему", command=self._login,
                               width=20)
        login_btn.pack(side=tk.LEFT, padx=(0, 20))

        exit_btn = ttk.Button(button_frame, text="Выход", command=self.window.quit,
                              width=20)
        exit_btn.pack(side=tk.LEFT)

        self.status_label = tk.Label(main_frame, text="Выберите роль и нажмите Войти",
                                     font=('Arial', 10), fg='gray')
        self.status_label.pack(pady=(20, 0))

    def _login(self):
        role = self.role_var.get()
        print(f"[DEBUG] Выбрана роль: {role}")
        self.status_label.config(text=f"Вход как {role}...", fg='blue')
        self.window.update()

        callback = self.on_login_success
        self.window.destroy()
        callback(role)

    def run(self):
        self.window.mainloop()