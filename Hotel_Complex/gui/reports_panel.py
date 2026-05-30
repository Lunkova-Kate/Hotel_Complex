import tkinter as tk
from tkinter import ttk, messagebox
from gui.sizes import REPORTS_PANEL
from gui.utils import center_window
from gui.formatter import DataFormatter
from gui.report_view import ReportView


class ReportsPanel:
    """Панель отчётов с автоматическим выполнением отчётов без параметров."""

    REPORTS_CONFIG = [
        ('1', 'Фирмы с объёмом броней >= N',
         'Организации, забронировавшие не менее указанного количества мест',
         'Партнёры', True),
        ('2', 'Постояльцы по характеристикам номера',
         'Гости, заселявшиеся в номера с указанной звёздностью и вместимостью',
         'Клиенты', True),
        ('3', 'Количество свободных номеров сейчас',
         'Подсчёт незанятых номеров на текущий момент',
         'Номера', False),
        ('4', 'Свободные номера с характеристиками',
         'Поиск свободных номеров по звёздности и вместимости',
         'Номера', True),
        ('5', 'Информация о конкретном номере',
         'Характеристики, свобода, ближайшее заселение',
         'Номера', True),
        ('6', 'Номера, освобождающиеся к сроку',
         'Занятые номера, которые освободятся к указанному времени',
         'Номера', True),
        ('7', 'Объём бронирования фирмой',
         'Статистика бронирований и предпочтения по типам номеров',
         'Партнёры', True),
        ('8', 'Недовольные клиенты и жалобы',
         'Клиенты с жалобами или низкими оценками',
         'Клиенты', False),
        ('9', 'Рентабельность корпусов',
         'Соотношение выручки к расходам корпусов за период',
         'Бизнес', True),
        ('10', 'Постояльцы из заданного номера',
         'Счета, жалобы и услуги гостей конкретного номера',
         'Клиенты', True),
        ('11', 'Фирмы с договорами в период',
         'Организации с действующими договорами',
         'Партнёры', True),
        ('12', 'Частые посетители',
         'Рейтинг клиентов по количеству визитов',
         'Клиенты', False),
        ('13', 'Новые клиенты за период',
         'Клиенты, зарегистрированные за указанный период',
         'Клиенты', True),
        ('14', 'Полная история клиента',
         'Все визиты, номера, счета и платежи клиента',
         'Клиенты', True),
        ('15', 'Кто занимал номер в период',
         'Постояльцы конкретного номера за период',
         'Номера', True),
        ('16', 'Процент партнёрских броней',
         'Доля бронирований через организации-партнёры',
         'Бизнес', False),
    ]

    def __init__(self, parent, business_logic):
        self.parent = parent
        self.bl = business_logic
        self.instant_results_cache = {}

        self.window = tk.Toplevel(parent)
        self.window.title("Отчёты и аналитика")
        self.window.resizable(True, True)

        width = REPORTS_PANEL['width']
        height = REPORTS_PANEL['height']
        self.window.geometry(f"{width}x{height}")
        center_window(self.window, width, height)

        self.window.transient(parent)
        self.window.grab_set()

        self._create_widgets()
        self._select_first_category()

    def _create_widgets(self):
        """Создаёт основной интерфейс."""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True)


        header = ttk.Frame(main_frame, padding="10")
        header.pack(fill=tk.X)

        ttk.Label(header, text="Отчёты и аналитика", font=('Arial', 16, 'bold')).pack(anchor='w')
        ttk.Label(header, text="Отчёты без параметров выполняются автоматически",
                  font=('Arial', 9)).pack(anchor='w')

        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', padx=10)

        content = ttk.Frame(main_frame)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)


        left_panel = ttk.Frame(content, width=150)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)

        ttk.Label(left_panel, text="Категории", font=('Arial', 11, 'bold')).pack(pady=(10, 10))

        categories = []
        seen = set()
        for _, _, _, cat, _ in self.REPORTS_CONFIG:
            if cat not in seen:
                categories.append(cat)
                seen.add(cat)

        self.category_buttons = {}
        for cat in categories:
            btn = ttk.Button(left_panel, text=cat, width=18,
                             command=lambda c=cat: self._show_category(c))
            btn.pack(pady=1, padx=5)
            self.category_buttons[cat] = btn


        ttk.Button(left_panel, text="Закрыть", command=self.window.destroy).pack(
            side=tk.BOTTOM, fill=tk.X, padx=5, pady=10)


        right_panel = ttk.Frame(content)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(right_panel, highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_panel, orient='vertical', command=self.canvas.yview)
        self.reports_frame = ttk.Frame(self.canvas)

        self.reports_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.reports_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._bind_mousewheel()
        self.canvas.bind('<Configure>', self._on_canvas_configure)

    def _bind_mousewheel(self):
        """Привязка колесика мыши."""

        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def on_mousewheel_linux(event):
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")

        self.canvas.bind("<Enter>", lambda e: (
            self.canvas.bind_all("<MouseWheel>", on_mousewheel),
            self.canvas.bind_all("<Button-4>", on_mousewheel_linux),
            self.canvas.bind_all("<Button-5>", on_mousewheel_linux)
        ))
        self.canvas.bind("<Leave>", lambda e: (
            self.canvas.unbind_all("<MouseWheel>"),
            self.canvas.unbind_all("<Button-4>"),
            self.canvas.unbind_all("<Button-5>")
        ))

    def _on_canvas_configure(self, event):
        """Подгоняет ширину."""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _select_first_category(self):
        """Выбирает первую категорию."""
        if self.category_buttons:
            first_cat = list(self.category_buttons.keys())[0]
            self._show_category(first_cat)

    def _show_category(self, category):
        """Показывает отчёты категории."""
        for widget in self.reports_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.reports_frame, text=category, font=('Arial', 14, 'bold')).pack(
            anchor='w', pady=(5, 10))

        category_reports = [r for r in self.REPORTS_CONFIG if r[3] == category]

        for report_id, name, description, cat, has_params in category_reports:
            self._create_report_card(report_id, name, description, has_params)

    def _create_report_card(self, report_id, name, description, has_params):
        """Создаёт карточку отчёта."""

        card = ttk.Frame(self.reports_frame, relief='solid', borderwidth=1)
        card.pack(fill=tk.X, pady=4, padx=5)

        title_frame = ttk.Frame(card, padding="10")
        title_frame.pack(fill=tk.X)

        text_frame = ttk.Frame(title_frame)
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        title_text = f"{report_id}. {name}"
        if not has_params:
            title_text += " (авто)"

        ttk.Label(text_frame, text=title_text, font=('Arial', 11, 'bold')).pack(anchor='w')
        ttk.Label(text_frame, text=description, font=('Arial', 8)).pack(anchor='w')

        btn_frame = ttk.Frame(title_frame)
        btn_frame.pack(side=tk.RIGHT)

        if has_params:
            ttk.Button(btn_frame, text="Запустить",
                       command=lambda rid=report_id: self._run_report_with_params(rid),
                       width=12).pack()
        else:
            ttk.Button(btn_frame, text="Обновить",
                       command=lambda rid=report_id: self._refresh_card(rid),
                       width=10).pack(side=tk.LEFT, padx=2)
            ttk.Button(btn_frame, text="Открыть полностью",
                       command=lambda rid=report_id, rname=name: self._open_full_report(rid, rname),
                       width=18).pack(side=tk.LEFT, padx=2)

        if not has_params:
            ttk.Separator(card, orient='horizontal').pack(fill='x')

            self.result_frame = ttk.Frame(card, padding="10")
            self.result_frame.pack(fill=tk.X)

            self._load_compact_result(self.result_frame, report_id, name)

    def _load_compact_result(self, parent, report_id, report_name):
        """Загружает и показывает результат."""
        try:
            func_name = self._get_func_name(report_id)
            if not func_name:
                ttk.Label(parent, text="Функция не найдена").pack(pady=5)
                return

            func = getattr(self.bl, func_name)
            result = func()

            self.instant_results_cache[report_id] = {
                'name': report_name,
                'result': result
            }

            self._display_compact_data(parent, result)

        except Exception as e:
            ttk.Label(parent, text=f"Ошибка: {str(e)[:80]}").pack(pady=5)

    def _display_compact_data(self, parent, data):
        """Отображает данные компактно."""
        for widget in parent.winfo_children():
            widget.destroy()

        if data is None or (isinstance(data, (list, dict)) and len(data) == 0):
            ttk.Label(parent, text="Нет данных", font=('Arial', 9, 'italic')).pack(pady=5)
            return

        if isinstance(data, (int, float)):
            display = f"{data:,.2f}".replace(',', ' ') if isinstance(data, float) else str(data)
            ttk.Label(parent, text=f"Значение: {display}", font=('Arial', 12, 'bold')).pack(pady=5)

        elif isinstance(data, dict):
            items = [(k, v) for k, v in data.items() if not k.lower().endswith('_id')]
            for key, value in items[:5]:
                row = ttk.Frame(parent)
                row.pack(fill='x', pady=1)

                pretty_key = DataFormatter.get_report_label(key)
                ttk.Label(row, text=f"{pretty_key}:", font=('Arial', 9, 'bold'),
                          width=22, anchor='e').pack(side=tk.LEFT, padx=5)

                if isinstance(value, bool):
                    value = 'Да' if value else 'Нет'
                elif value is None:
                    value = '—'
                elif isinstance(value, float):
                    value = f"{value:,.2f}".replace(',', ' ')

                ttk.Label(row, text=str(value), font=('Arial', 9)).pack(side=tk.LEFT, padx=5)

        elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            ttk.Label(parent, text=f"Найдено записей: {len(data)}",
                      font=('Arial', 9, 'bold')).pack(anchor='w', pady=(0, 5))

            raw_columns = list(data[0].keys())
            columns = [c for c in raw_columns if not c.lower().endswith('_id')][:3]

            if columns:
                for row in data[:3]:
                    text_parts = []
                    for col in columns:
                        val = row.get(col, '')
                        if isinstance(val, float):
                            val = f"{val:.0f}"
                        text_parts.append(str(val)[:25])

                    ttk.Label(parent, text=" | ".join(text_parts), font=('Arial', 8)).pack(
                        anchor='w', padx=10, pady=1)

            if len(data) > 3:
                ttk.Label(parent, text=f"... и ещё {len(data) - 3} записей",
                          font=('Arial', 8, 'italic')).pack(anchor='w', pady=(3, 0))

        elif isinstance(data, tuple) and len(data) == 2:
            summary, preferences = data
            if summary:
                for key, value in summary.items():
                    pretty_key = DataFormatter.get_report_label(key)
                    ttk.Label(parent, text=f"{pretty_key}: {value}", font=('Arial', 9)).pack(
                        anchor='w', padx=10)
            if preferences:
                ttk.Label(parent, text=f"Предпочтений: {len(preferences)}", font=('Arial', 9)).pack(
                    anchor='w', padx=10, pady=(5, 0))

        else:
            ttk.Label(parent, text=str(data)[:200], font=('Arial', 9), wraplength=500).pack(pady=5)

    def _refresh_card(self, report_id):
        """Обновляет карточку."""
        for widget in self.reports_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Frame) and child.winfo_children():
                        for w in child.winfo_children():
                            w.destroy()

                        for rid, name, desc, cat, hp in self.REPORTS_CONFIG:
                            if rid == report_id:
                                self._load_compact_result(child, rid, name)
                                return

    def _open_full_report(self, report_id, report_name):
        """Открывает полный отчёт."""
        cached = self.instant_results_cache.get(report_id)

        if cached and cached['result'] is not None:
            ReportView(self.window, report_name, cached['result'])
        else:
            try:
                func_name = self._get_func_name(report_id)
                func = getattr(self.bl, func_name)
                result = func()
                ReportView(self.window, report_name, result)
            except Exception as e:
                messagebox.showerror("Ошибка", str(e), parent=self.window)

    def _run_report_with_params(self, report_id):
        """Открывает форму с параметрами."""
        from gui.query_dialog import QueryDialog
        QueryDialog(self.window, self.bl, report_id)

    def _get_func_name(self, report_id):
        """Получает имя функции."""
        from gui.query_dialog import QueryDialog
        report_info = QueryDialog.REPORTS.get(report_id, {})
        return report_info.get('func', '')