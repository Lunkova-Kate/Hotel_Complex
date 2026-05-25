import tkinter as tk
from tkinter import ttk, messagebox
from gui.utils import center_window
from gui.formatter import DataFormatter
from gui.sizes import REPORTS_PANEL


class ReportView:
    """Окно для отображения результатов отчёта с полной поддержкой ООП-форматирования."""

    def __init__(self, parent, title, data):

        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title(f"Отчёт: {title}")


        width = REPORTS_PANEL['width']
        height = REPORTS_PANEL['height']
        self.window.geometry(f"{width}x{height}")
        center_window(self.window, width, height)

        # Делаем окно немодальным, но поверх родителя
        self.window.transient(parent)
        self.window.grab_set()

        self._display(data)

    def _display(self, data):

        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        if data is None:
            self._show_empty(main_frame)
            return

        if isinstance(data, (int, float)):
            self._show_number(main_frame, data)
            return

        if isinstance(data, dict) and not isinstance(data, list):
            if not data:
                self._show_empty(main_frame)
                return
            self._display_dict(data, main_frame)
            return

        if isinstance(data, list) and data and isinstance(data[0], dict):
            self._display_table(data, main_frame)
        elif isinstance(data, tuple) and len(data) == 2:

            summary, preferences = data
            self._display_tuple_result(summary, preferences, main_frame)
        elif isinstance(data, list):

            self._display_list(data, main_frame)
        else:
            self._show_text(main_frame, str(data))

    def _show_empty(self, parent):


        for widget in parent.winfo_children():
            widget.destroy()
        #print ('IM HERE')

        center_frame = ttk.Frame(parent)
        center_frame.pack(expand=True)

        tk.Label(center_frame, text="📭", font=('Arial', 64)).pack(pady=10)

        tk.Label(center_frame, text="По вашему запросу ничего не найдено",
                 font=('Arial', 14, 'bold'), fg='#555555').pack(pady=5)

        tk.Label(center_frame, text="В базе данных нет записей, соответствующих заданным параметрам.",
                 font=('Arial', 10), fg='gray').pack(pady=(0, 20))

        ttk.Button(center_frame, text="Понятно, закрыть",
                   command=self.window.destroy, width=20).pack()

    def _display_tuple_result(self, summary, preferences, parent):

        if not summary or (summary.get('bookings_count') == 0 and summary.get('total_rooms_booked') == 0):
            self._show_empty(parent)
            return

        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')

        tk.Label(scrollable_frame, text="Анализ бронирований организации",
                 font=('Arial', 14, 'bold')).pack(pady=10)


        summary_frame = ttk.LabelFrame(scrollable_frame, text="Сводка по бронированиям ", padding="15")
        summary_frame.pack(fill='x', padx=20, pady=10)

        summary_labels = {
            'bookings_count': ('Количество броней', 'шт.'),
            'total_rooms_booked': ('Всего номеров забронировано', 'шт.'),
            'total_people_booked': ('Всего человек зарезервировано', 'чел.')
        }

        for key, (label, unit) in summary_labels.items():
            value = summary.get(key, 0) if summary else 0
            row_frame = ttk.Frame(summary_frame)
            row_frame.pack(fill='x', pady=5)

            tk.Label(row_frame, text=f"{label}:", font=('Arial', 10, 'bold'),
                     width=35, anchor='e').pack(side=tk.LEFT, padx=5)
            tk.Label(row_frame, text=f"{value} {unit}", font=('Arial', 10),
                     fg='blue').pack(side=tk.LEFT, padx=5)


        if preferences:
            pref_frame = ttk.LabelFrame(scrollable_frame, text="Предпочтения по типам номеров ", padding="15")
            pref_frame.pack(fill='both', expand=True, padx=20, pady=10)

            columns = ['room_type', 'times_selected', 'percentage']
            tree = ttk.Treeview(pref_frame, columns=columns, show='headings', height=10)

            tree.heading('room_type', text='Тип номера')
            tree.heading('times_selected', text='Кол-во выборов')
            tree.heading('percentage', text='Доля (%)')

            tree.column('room_type', width=250)
            tree.column('times_selected', width=120, anchor='center')
            tree.column('percentage', width=100, anchor='center')

            v_scroll = ttk.Scrollbar(pref_frame, orient='vertical', command=tree.yview)
            tree.configure(yscrollcommand=v_scroll.set)

            tree.pack(side=tk.LEFT, fill='both', expand=True)
            v_scroll.pack(side=tk.RIGHT, fill='y')

            for row in preferences:
                tree.insert('', 'end', values=(
                    row.get('room_type', 'Неизвестно'),
                    row.get('times_selected', 0),
                    f"{row.get('percentage', 0)}%"
                ))
        else:
            tk.Label(scrollable_frame, text="📭 Нет данных о предпочтениях по типам комнат",
                     font=('Arial', 10, 'italic'), fg='gray').pack(pady=20)

        ttk.Button(scrollable_frame, text="Закрыть окно отчёта", command=self.window.destroy).pack(pady=20)

    def _show_number(self, parent, number):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Результат расчета:", font=('Arial', 14)).pack(pady=10)
        tk.Label(frame, text=str(number), font=('Arial', 24, 'bold'), fg='blue').pack(pady=10)

        ttk.Button(frame, text="Закрыть", command=self.window.destroy).pack(pady=20)

    def _show_text(self, parent, text):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(frame, wrap='word', font=('Courier', 10))
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')

        text_widget.insert('1.0', text)
        text_widget.config(state='disabled')

    def _display(self, data):
        #print(f"[DEBUG] _display called, data type: {type(data)}, data: {str(data)[:100]}")

        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)


        if data is None:
           # print("[DEBUG] data is None -> _show_empty")
            self._show_empty(main_frame)
            return

        if isinstance(data, (int, float)):
           # print(f"[DEBUG] data is number: {data}")
            self._show_number(main_frame, data)
            return

        if isinstance(data, dict):
            if not data:
               # print("[DEBUG] data is empty dict -> _show_empty")
                self._show_empty(main_frame)
                return
            #print("[DEBUG] data is dict -> _display_dict")
            self._display_dict(data, main_frame)
            return

        if isinstance(data, list):
            if len(data) == 0:
               # print("[DEBUG] data is empty list -> _show_empty")
                self._show_empty(main_frame)
                return
            if isinstance(data[0], dict):
               # print(f"[DEBUG] data is list of dicts, len={len(data)} -> _display_table")
                self._display_table(data, main_frame)
                return
            else:
               # print("[DEBUG] data is flat list -> _display_list")
                self._display_list(data, main_frame)
                return

        if isinstance(data, tuple) and len(data) == 2:
            #print("[DEBUG] data is tuple -> _display_tuple_result")
            summary, preferences = data
            self._display_tuple_result(summary, preferences, main_frame)
            return

        #Fprint(f"[DEBUG] Unknown type -> _show_text")
        self._show_text(main_frame, str(data))


    def _display_list(self, data, parent):

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)

        listbox = tk.Listbox(frame, font=('Arial', 10))
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)

        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')

        for item in data:
            listbox.insert(tk.END, str(item))

    def _display_table(self, data, parent):

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)

        info_label = tk.Label(frame, text=f"Найдено записей: {len(data)}",
                              font=('Arial', 11, 'bold'), fg='green')
        info_label.pack(pady=5)

        table_frame = ttk.Frame(frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=5)


        raw_columns = list(data[0].keys())
        columns = [col for col in raw_columns if not (col.lower().endswith('_id') or col.lower() == 'id')]

        tree = ttk.Treeview(table_frame, columns=columns, show='headings')

        for col in columns:
            pretty_label = DataFormatter.get_report_label(col)
            tree.heading(col, text=pretty_label)
            tree.column(col, width=160, anchor='center' if 'amount' in col else 'w')

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

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Закрыть", command=self.window.destroy).pack(side='left', padx=10)

        def copy_to_clipboard():
            text = '\t'.join([DataFormatter.get_report_label(c) for c in columns]) + '\n'
            for row in data:
                row_vals = []
                for col in columns:
                    val = row.get(col, '')
                    if val is None: val = '—'
                    row_vals.append(str(val))
                text += '\t'.join(row_vals) + '\n'
            self.window.clipboard_clear()
            self.window.clipboard_append(text)
            messagebox.showinfo("Копирование", "Данные успешно скопированы в буфер обмена!")

        ttk.Button(btn_frame, text="Копировать таблицу", command=copy_to_clipboard).pack(side='left', padx=10)