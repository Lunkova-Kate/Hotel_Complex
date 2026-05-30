import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'Core'))
sys.path.insert(0, os.path.join(BASE_DIR, 'Data_Acces'))


def start_app(role):
    """Запуск главного окна после авторизации."""
    print(f"[DEBUG] start_app вызван с ролью: {role}")
    try:
        from gui.main_window import MainWindow
        print("[DEBUG] MainWindow импортирован")
        app = MainWindow(role)
        print("[DEBUG] MainWindow создан, запускаем...")
        app.run()
        print("[DEBUG] MainWindow.run() завершён")
    except Exception as e:
        print(f"[ERROR] Ошибка в start_app: {e}")
        import traceback
        traceback.print_exc()
        input("Нажмите Enter для выхода...")


if __name__ == "__main__":
    print("[DEBUG] Запуск main.py")
    try:
        from gui.auth_window import AuthWindow
        print("[DEBUG] AuthWindow импортирован")
        auth = AuthWindow(start_app)
        print("[DEBUG] AuthWindow создан, запускаем...")
        auth.run()
        print("[DEBUG] AuthWindow.run() завершён")
    except Exception as e:
        print(f"[ERROR] Ошибка в main: {e}")
        import traceback
        traceback.print_exc()
        input("Нажмите Enter для выхода...")