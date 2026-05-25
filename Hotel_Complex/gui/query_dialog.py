# gui/query_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from gui.sizes import QUERY_DIALOG
from gui.utils import center_window
from gui.report_view import ReportView


class QueryDialog:
    """Диалог для выполнения отчёта с параметрами."""


    REPORTS = {
        '1': {
            'name': 'Фирмы с объёмом броней ≥ N',
            'func': 'report_firms_by_volume',
            'params': [
                {'name': 'min_people', 'label': 'Минимальное кол-во человек', 'type': 'int', 'required': True},
                {'name': 'start_date', 'label': 'Дата начала (опционально)', 'type': 'date', 'required': False},
                {'name': 'end_date', 'label': 'Дата окончания (опционально)', 'type': 'date', 'required': False},
            ]
        },
        '2': {
            'name': 'Постояльцы по характеристикам номера',
            'func': 'report_guests_by_room_features',
            'params': [
                {'name': 'stars', 'label': 'Звёздность (2-5)', 'type': 'int', 'required': True},
                {'name': 'min_capacity', 'label': 'Мин. вместимость', 'type': 'int', 'required': True},
                {'name': 'start_date', 'label': 'Дата начала', 'type': 'date', 'required': True},
                {'name': 'end_date', 'label': 'Дата окончания', 'type': 'date', 'required': True},
            ]
        },
        '3': {
            'name': 'Количество свободных номеров сейчас',
            'func': 'report_free_rooms_count',
            'params': []
        },
        '4': {
            'name': 'Свободные номера с характеристиками',
            'func': 'report_free_rooms_by_features',
            'params': [
                {'name': 'stars', 'label': 'Звёздность (2-5)', 'type': 'int', 'required': True},
                {'name': 'min_capacity', 'label': 'Мин. вместимость', 'type': 'int', 'required': True},
                {'name': 'moment', 'label': 'Момент времени', 'type': 'timestamp', 'required': True},
            ]
        },
        '5': {
            'name': 'Информация о номере',
            'func': 'report_room_free_info',
            'params': [
                {'name': 'room_id', 'label': 'ID номера', 'type': 'int', 'required': True},
            ]
        },
        '6': {
            'name': 'Занятые номера, освобождающиеся к сроку',
            'func': 'report_occupied_rooms_free_by_deadline',
            'params': [
                {'name': 'reference_ts', 'label': 'Опорный момент', 'type': 'timestamp', 'required': True},
                {'name': 'deadline_ts', 'label': 'Крайний срок', 'type': 'timestamp', 'required': True},
            ]
        },
        '7': {
            'name': 'Объём бронирования фирмой и предпочтения',
            'func': 'report_booking_volume_and_preferences',
            'params': [
                {'name': 'org_name', 'label': 'Название организации', 'type': 'str', 'required': True},
                {'name': 'start_date', 'label': 'Дата начала', 'type': 'date', 'required': True},
                {'name': 'end_date', 'label': 'Дата окончания', 'type': 'date', 'required': True},
            ]
        },
        '8': {
            'name': 'Недовольные клиенты и жалобы',
            'func': 'report_unhappy_clients',
            'params': []
        },
        '9': {
            'name': 'Рентабельность корпусов',
            'func': 'report_profitability',
            'params': [
                {'name': 'start_date', 'label': 'Дата начала', 'type': 'date', 'required': True},
                {'name': 'end_date', 'label': 'Дата окончания', 'type': 'date', 'required': True},
            ]
        },
        '10': {
            'name': 'Сведения о постояльцах из номера',
            'func': 'report_guest_info_by_room',
            'params': [
                {'name': 'room_id', 'label': 'ID номера', 'type': 'int', 'required': True},
            ]
        },
        '11': {
            'name': 'Фирмы с договорами в период',
            'func': 'report_firms_with_contracts_period',
            'params': [
                {'name': 'start_date', 'label': 'Дата начала', 'type': 'date', 'required': True},
                {'name': 'end_date', 'label': 'Дата окончания', 'type': 'date', 'required': True},
            ]
        },
        '12': {
            'name': 'Частые посетители (все корпуса)',
            'func': 'report_frequent_guests_all',
            'params': []
        },
        '13': {
            'name': 'Новые клиенты за период',
            'func': 'report_new_clients',
            'params': [
                {'name': 'start_date', 'label': 'Дата начала', 'type': 'date', 'required': True},
                {'name': 'end_date', 'label': 'Дата окончания', 'type': 'date', 'required': True},
            ]
        },
        '14': {
            'name': 'Полная история клиента',
            'func': 'report_client_full_history',
            'params': [
                {'name': 'client_id', 'label': 'ID клиента', 'type': 'int', 'required': True},
            ]
        },
        '15': {
            'name': 'Кто занимал номер в период',
            'func': 'report_room_occupants',
            'params': [
                {'name': 'room_id', 'label': 'ID номера', 'type': 'int', 'required': True},
                {'name': 'start_ts', 'label': 'Начало периода', 'type': 'timestamp', 'required': True},
                {'name': 'end_ts', 'label': 'Конец периода', 'type': 'timestamp', 'required': True},
            ]
        },
        '16': {
            'name': 'Процент партнёрских броней',
            'func': 'report_partner_percentage',
            'params': []
        },
    }

    def __init__(self, parent, business_logic, report_id, on_run=None):
        self.parent = parent
        self.bl = business_logic
        self.report_id = report_id
        self.report_info = self.REPORTS.get(report_id)
        self.on_run = on_run
        self.entries = {}

        if not self.report_info:
            raise ValueError(f"Неизвестный отчёт: {report_id}")

        self.window = tk.Toplevel(parent)
        self.window.title(self.report_info['name'])
        self.window.resizable(False, False)
        self.window.transient(parent)

        self._create_widgets()


        width = QUERY_DIALOG['width']
        height = QUERY_DIALOG['height']
        center_window(self.window, width, height)
        self.window.grab_set()

    def _create_widgets(self):

        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = tk.Label(main_frame, text=self.report_info['name'],
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))

        params_frame = ttk.Frame(main_frame)
        params_frame.pack(fill=tk.BOTH, expand=True)


        canvas = tk.Canvas(params_frame)
        scrollbar = ttk.Scrollbar(params_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')

        row = 0
        for param in self.report_info['params']:
            label = param['label']
            name = param['name']
            param_type = param['type']
            required = param.get('required', False)
            default = param.get('default', '')


            param_frame = ttk.Frame(scrollable_frame)
            param_frame.pack(fill='x', pady=8)


            label_text = f"{label}{' *' if required else ':'}"
            tk.Label(param_frame, text=label_text, font=('Arial', 10),
                     width=25, anchor='e').pack(side=tk.LEFT, padx=5)

            if param_type in ('date', 'timestamp'):
                entry_frame = ttk.Frame(param_frame)
                entry_frame.pack(side=tk.LEFT, padx=5)

                entry = ttk.Entry(entry_frame, width=30, font=('Arial', 10))
                entry.pack(side=tk.LEFT)

                if default:
                    entry.insert(0, default)
                elif param_type == 'date':
                    entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
                elif param_type == 'timestamp':
                    entry.insert(0, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

                hint = "(ГГГГ-ММ-ДД)" if param_type == 'date' else "(ГГГГ-ММ-ДД ЧЧ:ММ:СС)"
                tk.Label(entry_frame, text=hint, font=('Arial', 8),
                         fg='gray').pack(side=tk.LEFT, padx=5)

            elif param_type == 'int':
                entry = ttk.Entry(param_frame, width=30, font=('Arial', 10))
                entry.pack(side=tk.LEFT, padx=5)
                if default:
                    entry.insert(0, str(default))

            elif param_type == 'str':
                entry = ttk.Entry(param_frame, width=30, font=('Arial', 10))
                entry.pack(side=tk.LEFT, padx=5)
                if default:
                    entry.insert(0, default)

            else:
                entry = ttk.Entry(param_frame, width=30, font=('Arial', 10))
                entry.pack(side=tk.LEFT, padx=5)
                if default:
                    entry.insert(0, str(default))

            self.entries[name] = (entry, param_type, required)
            row += 1

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="▶ Выполнить", command=self._run,
                   width=15).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="✖ Отмена", command=self.window.destroy,
                   width=15).pack(side='left', padx=10)

        if not self.report_info['params']:
            info_label = tk.Label(scrollable_frame,
                                  text="Этот отчёт не требует параметров.\nНажмите 'Выполнить' для просмотра результата.",
                                  font=('Arial', 10), fg='green', justify='center')
            info_label.pack(pady=20)

    def _run(self):
        """Выполнить отчёт с введёнными параметрами."""
        try:
            kwargs = {}

            for name, (entry, param_type, required) in self.entries.items():
                value = entry.get().strip()

                if required and not value:
                    raise ValueError(f"Параметр '{name}' обязателен для заполнения")

                if not value:
                    kwargs[name] = None
                    continue

                if param_type == 'int':
                    try:
                        value = int(value)
                    except ValueError:
                        raise ValueError(f"Параметр '{name}' должен быть целым числом")

                elif param_type == 'date':
                    try:
                        datetime.strptime(value, '%Y-%m-%d')
                    except ValueError:
                        raise ValueError(f"Неверный формат даты для '{name}'. Используйте: ГГГГ-ММ-ДД")

                elif param_type == 'timestamp':
                    try:
                        datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        raise ValueError(f"Неверный формат даты/времени для '{name}'. Используйте: ГГГГ-ММ-ДД ЧЧ:ММ:СС")

                kwargs[name] = value

            func_name = self.report_info['func']
            if not hasattr(self.bl, func_name):
                raise ValueError(f"Функция {func_name} не найдена в BusinessLogic")

            func = getattr(self.bl, func_name)

            result = func(**kwargs)

            self.window.destroy()

            ReportView(self.parent, self.report_info['name'], result)

            if self.on_run:
                self.on_run()

        except ValueError as e:
            messagebox.showerror("Ошибка в параметрах", str(e), parent=self.window)
        except Exception as e:
            messagebox.showerror("Ошибка выполнения отчёта", str(e), parent=self.window)