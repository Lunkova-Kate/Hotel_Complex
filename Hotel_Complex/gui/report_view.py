import tkinter as tk
from tkinter import ttk, messagebox
from gui.sizes import REPORTS_PANEL
from gui.utils import center_window
from gui.formatter import DataFormatter


class ReportView:
    """Окно для отображения результатов отчёта."""

    def __init__(self, parent, title, data):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title(f"Отчёт: {title}")

        width = REPORTS_PANEL['width']
        height = REPORTS_PANEL['height']
        self.window.geometry(f"{width}x{height}")
        center_window(self.window, width, height)

        self.window.transient(parent)
        self.window.grab_set()

        self._display(data)

    def _display(self, data):
        """Определяет тип данных и вызывает нужный метод."""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        if data is None:
            self._show_empty(main_frame)
            return

        if isinstance(data, (int, float)):
            self._show_number(main_frame, data)
            return

        if isinstance(data, dict):
            if not data:
                self._show_empty(main_frame)
                return
            self._display_dict(data, main_frame)
            return

        if isinstance(data, list):
            if len(data) == 0:
                self._show_empty(main_frame)
                return
            if isinstance(data[0], dict):
                self._display_table(data, main_frame)
            else:
                self._display_list(data, main_frame)
            return

        if isinstance(data, tuple) and len(data) == 2:
            summary, preferences = data
            self._display_tuple_result(summary, preferences, main_frame)
            return

        self._show_text(main_frame, str(data))

    def _show_empty(self, parent):
        """Показать сообщение о пустом результате."""
        for widget in parent.winfo_children():
            widget.destroy()

        center_frame = ttk.Frame(parent)
        center_frame.pack(expand=True)

        tk.Label(center_frame, text="📭", font=('Arial', 64)).pack(pady=10)
        tk.Label(center_frame, text="По вашему запросу ничего не найдено",
                 font=('Arial', 14, 'bold'), fg='#555555').pack(pady=5)
        tk.Label(center_frame, text="В базе данных нет записей, соответствующих заданным параметрам.",
                 font=('Arial', 10), fg='gray').pack(pady=(0, 20))
        ttk.Button(center_frame, text="Понятно, закрыть",
                   command=self.window.destroy, width=20).pack()

    def _show_number(self, parent, number):
        for widget in parent.winfo_children():
            widget.destroy()

        center_frame = ttk.Frame(parent)
        center_frame.pack(expand=True)

        tk.Label(center_frame, text="Результат:", font=('Arial', 14)).pack(pady=10)
        tk.Label(center_frame, text=str(number), font=('Arial', 24, 'bold'),
                 fg='blue').pack(pady=10)
        ttk.Button(center_frame, text="Закрыть",
                   command=self.window.destroy).pack(pady=20)

    def _show_text(self, parent, text):
        for widget in parent.winfo_children():
            widget.destroy()

        text_widget = tk.Text(parent, wrap='word', font=('Courier', 10))
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')

        text_widget.insert('1.0', text)
        text_widget.config(state='disabled')

    def _display_dict(self, data, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>",
                              lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')

        tk.Label(scrollable_frame, text="Детальная информация:",
                 font=('Arial', 12, 'bold')).pack(pady=10)

        for key, value in data.items():
            pretty_key = DataFormatter.get_report_label(key)
            row_frame = ttk.Frame(scrollable_frame)
            row_frame.pack(fill='x', padx=20, pady=5)

            tk.Label(row_frame, text=f"{pretty_key}:", font=('Arial', 10, 'bold'),
                     width=30, anchor='e').pack(side=tk.LEFT, padx=5)

            if isinstance(value, bool):
                value = 'Да' if value else 'Нет'
            elif value is None:
                value = '—'

            tk.Label(row_frame, text=str(value), font=('Arial', 10),
                     wraplength=500, justify='left').pack(side=tk.LEFT, padx=5)

        ttk.Button(scrollable_frame, text="Закрыть",
                   command=self.window.destroy).pack(pady=20)

    def _display_list(self, data, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        listbox = tk.Listbox(parent, font=('Arial', 10))
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)

        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')

        for item in data:
            listbox.insert(tk.END, str(item))

    def _display_table(self, data, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        info_label = tk.Label(parent, text=f"📋 Найдено записей: {len(data)}",
                              font=('Arial', 11, 'bold'), fg='green')
        info_label.pack(pady=5)

        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        raw_columns = list(data[0].keys())
        columns = [col for col in raw_columns if not (col.lower().endswith('_id') or col.lower() == 'id')]

        tree = ttk.Treeview(table_frame, columns=columns, show='headings')

        for col in columns:
            pretty_label = DataFormatter.get_report_label(col)
            tree.heading(col, text=pretty_label)
            tree.column(col, width=160, anchor='center')

        v_scroll = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        h_scroll = ttk.Scrollbar(table_frame, orient='horizontal', command=tree.xview)
        tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        for row in data:
            values = []
            for col in columns:
                val = row.get(col, '')
                if isinstance(val, bool):
                    val = 'Да' if val else 'Нет'
                elif val is None:
                    val = '—'
                values.append(str(val))
            tree.insert('', 'end', values=values)

        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Закрыть",
                   command=self.window.destroy).pack(side='left', padx=10)

        def copy_to_clipboard():
            text = '\t'.join([DataFormatter.get_report_label(c) for c in columns]) + '\n'
            for row in data:
                row_vals = [str(row.get(col, '—')) for col in columns]
                text += '\t'.join(row_vals) + '\n'
            self.window.clipboard_clear()
            self.window.clipboard_append(text)
            messagebox.showinfo("Копирование", "Данные скопированы в буфер обмена!")

        ttk.Button(btn_frame, text="Копировать", command=copy_to_clipboard).pack(side='left', padx=10)

    def _display_tuple_result(self, summary, preferences, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>",
                              lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')

        tk.Label(scrollable_frame, text="Анализ бронирований организации",
                 font=('Arial', 14, 'bold')).pack(pady=10)

        summary_frame = ttk.LabelFrame(scrollable_frame, text=" Сводка ", padding="15")
        summary_frame.pack(fill='x', padx=20, pady=10)

        for key, (label, unit) in {
            'bookings_count': ('Количество броней', 'шт.'),
            'total_rooms_booked': ('Всего номеров', 'шт.'),
            'total_people_booked': ('Всего человек', 'чел.')
        }.items():
            value = summary.get(key, 0) if summary else 0
            row_frame = ttk.Frame(summary_frame)
            row_frame.pack(fill='x', pady=3)
            tk.Label(row_frame, text=f"{label}:", font=('Arial', 10, 'bold'),
                     width=30, anchor='e').pack(side=tk.LEFT, padx=5)
            tk.Label(row_frame, text=f"{value} {unit}", font=('Arial', 10),
                     fg='blue').pack(side=tk.LEFT, padx=5)

        if preferences:
            pref_frame = ttk.LabelFrame(scrollable_frame, text=" Предпочтения ", padding="15")
            pref_frame.pack(fill='both', expand=True, padx=20, pady=10)

            tree = ttk.Treeview(pref_frame, columns=['room_type', 'times_selected', 'percentage'],
                                show='headings', height=8)
            tree.heading('room_type', text='Тип номера')
            tree.heading('times_selected', text='Выбрано раз')
            tree.heading('percentage', text='Доля (%)')
            tree.column('room_type', width=200)
            tree.column('times_selected', width=100, anchor='center')
            tree.column('percentage', width=100, anchor='center')
            tree.pack(fill='both', expand=True)

            for row in preferences:
                tree.insert('', 'end', values=(
                    row.get('room_type', '—'),
                    row.get('times_selected', 0),
                    f"{row.get('percentage', 0)}%"
                ))

        ttk.Button(scrollable_frame, text="Закрыть",
                   command=self.window.destroy).pack(pady=20)