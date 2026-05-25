import tkinter as tk
from tkinter import ttk

from gui.sizes import REPORTS_PANEL
from gui.utils import center_window
from gui.report_view import ReportView


class ReportsPanel:

    REPORTS_CONFIG = [

        ('1', 'Фирмы с объёмом броней >= N',
         'Показывает организации, забронировавшие не менее указанного количества мест',
         'Партнёры', True),

        ('2', 'Постояльцы по характеристикам номера',
         'Список гостей, заселявшихся в номера с указанной звёздностью и вместимостью за период',
         'Клиенты', True),

        ('3', 'Количество свободных номеров сейчас',
         'Мгновенный подсчёт незанятых номеров на текущий момент',
         'Номера', False),

        ('4', 'Свободные номера с характеристиками',
         'Поиск свободных номеров по звёздности и вместимости на заданное время',
         'Номера', True),

        ('5', 'Информация о конкретном номере',
         'Детальные сведения о номере: характеристики, свобода, ближайшее заселение',
         'Номера', True),

        ('6', 'Номера, освобождающиеся к сроку',
         'Какие занятые номера освободятся к указанному времени',
         'Номера', True),

        ('7', 'Объём бронирования фирмой',
         'Статистика бронирований организации и предпочтения по типам номеров',
         'Партнёры', True),

        ('8', 'Недовольные клиенты и жалобы',
         'Список клиентов с жалобами или низкими оценками',
         'Клиенты', False),

        ('9', 'Рентабельность корпусов',
         'Соотношение выручки с номеров к расходам корпусов за период',
         'Бизнес', True),

        ('10', 'Постояльцы из заданного номера',
         'Счета, жалобы и использованные услуги гостей конкретного номера',
         'Клиенты', True),

        ('11', 'Фирмы с договорами в период',
         'Организации, чьи договоры действуют в указанный период',
         'Партнёры', True),

        ('12', 'Частые посетители',
         'Рейтинг клиентов по количеству визитов во все корпуса',
         'Клиенты', False),

        ('13', 'Новые клиенты за период',
         'Клиенты, зарегистрированные в системе за указанный период',
         'Клиенты', True),

        ('14', 'Полная история клиента',
         'Все визиты, номера, счета и платежи конкретного человека',
         'Клиенты', True),

        ('15', 'Кто занимал номер в период',
         'Постояльцы, проживавшие в конкретном номере в заданный период',
         'Номера', True),

        ('16', 'Процент партнёрских броней',
         'Доля бронирований, сделанных через организации-партнёры',
         'Бизнес', False),
    ]

    def __init__(self, parent, business_logic):
        self.parent = parent
        self.bl = business_logic

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
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(main_frame, padding="15")
        header.pack(fill=tk.X)

        tk.Label(header, text="Отчёты и аналитика",
                 font=('Arial', 16, 'bold'), fg='#2c3e50').pack(anchor='w')
        tk.Label(header, text="Выберите отчёт из списка. Отчёты без параметров запускаются мгновенно.",
                 font=('Arial', 9), fg='gray').pack(anchor='w', pady=(5, 0))

        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', padx=10)


        content = ttk.Frame(main_frame)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


        left_panel = ttk.Frame(content, width=180)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)

        tk.Label(left_panel, text="Категории", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 10))


        categories = []
        seen = set()
        for _, _, _, cat, _ in self.REPORTS_CONFIG:
            if cat not in seen:
                categories.append(cat)
                seen.add(cat)

        self.category_buttons = {}
        for cat in categories:
            btn = ttk.Button(left_panel, text=cat,
                             command=lambda c=cat: self._show_category(c))
            btn.pack(fill=tk.X, pady=2)
            self.category_buttons[cat] = btn

        right_panel = ttk.Frame(content)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.reports_frame = ttk.Frame(right_panel)
        self.reports_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Button(main_frame, text="Закрыть", command=self.window.destroy,
                   width=15).pack(pady=10)

    def _select_first_category(self):

        if self.category_buttons:
            first_cat = list(self.category_buttons.keys())[0]
            self._show_category(first_cat)

    def _show_category(self, category):

        for widget in self.reports_frame.winfo_children():
            widget.destroy()

        for cat, btn in self.category_buttons.items():
            if cat == category:
                btn.configure(style='')
            else:
                btn.configure(style='')


        tk.Label(self.reports_frame, text=category,
                 font=('Arial', 14, 'bold'), fg='#2c3e50').pack(anchor='w', pady=(0, 15))


        category_reports = [r for r in self.REPORTS_CONFIG if r[3] == category]


        for report_id, name, description, cat, has_params in category_reports:
            self._create_report_card(report_id, name, description, has_params)

    def _create_report_card(self, report_id, name, description, has_params):

        card = ttk.Frame(self.reports_frame, relief='solid', borderwidth=1)
        card.pack(fill=tk.X, pady=5, padx=5)


        inner = ttk.Frame(card, padding="12")
        inner.pack(fill=tk.X)

        text_frame = ttk.Frame(inner)
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        title_text = f"{report_id}. {name}"
        title_label = tk.Label(text_frame, text=title_text,
                               font=('Arial', 11, 'bold'), fg='#2c3e50',
                               anchor='w', justify='left')
        title_label.pack(anchor='w')

        desc_label = tk.Label(text_frame, text=description,
                              font=('Arial', 9), fg='gray',
                              anchor='w', justify='left', wraplength=450)
        desc_label.pack(anchor='w', pady=(3, 0))

        btn_frame = ttk.Frame(inner)
        btn_frame.pack(side=tk.RIGHT, padx=(10, 0))

        if has_params:

            run_btn = ttk.Button(btn_frame, text="Запустить",
                                 command=lambda: self._run_report_with_params(report_id, name))
            run_btn.pack()
        else:
            instant_btn = ttk.Button(btn_frame, text="Показать",
                                     command=lambda rid=report_id, rname=name: self._run_report_instant(rid, rname))
            instant_btn.pack()

    def _run_report_instant(self, report_id, report_name):

        try:
            func_name = self._get_func_name(report_id)
            func = getattr(self.bl, func_name)
            result = func()
            ReportView(self.window, report_name, result)
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Ошибка отчёта", str(e), parent=self.window)

    def _run_report_with_params(self, report_id, report_name):

        from gui.query_dialog import QueryDialog
        QueryDialog(self.window, self.bl, report_id)

    def _get_func_name(self, report_id):

        from gui.query_dialog import QueryDialog
        report_info = QueryDialog.REPORTS.get(report_id, {})
        return report_info.get('func', '')