import tkinter as tk
from tkinter import ttk
from gui.formatter import DataFormatter


class PaginatedTableView(ttk.Frame):
    """Таблица с пагинацией, сортировкой и двойным кликом."""

    def __init__(self, parent, business_logic, table_name, columns_meta,
                 per_page=50, on_select=None, on_double_click=None):
        super().__init__(parent)
        self.bl = business_logic
        self.table_name = table_name
        self.columns_meta = columns_meta
        self.per_page = per_page
        self.on_select = on_select
        self.on_double_click = on_double_click

        self.current_page = 1
        self.total_pages = 1
        self.total_records = 0
        self.raw_records = []


        self.sort_column = None       # имя колонки, по которой сортируем
        self.sort_reverse = False     # False = по возрастанию, True = по убыванию

        self._create_widgets()


    # ИНТЕРФЕЙС


    def _create_widgets(self):
        # Верхняя панель с информацией
        info_frame = ttk.Frame(self)
        info_frame.pack(fill=tk.X, pady=(0, 5))

        self.info_label = tk.Label(info_frame, text="Загрузка...",
                                   font=('Arial', 10))
        self.info_label.pack(side=tk.LEFT)

        # Выбор количества записей на странице
        ttk.Label(info_frame, text="Записей на странице:").pack(side=tk.RIGHT, padx=5)
        self.per_page_var = tk.StringVar(value=str(self.per_page))
        per_page_combo = ttk.Combobox(info_frame, textvariable=self.per_page_var,
                                      values=['25', '50', '100', '200'],
                                      state='readonly', width=5)
        per_page_combo.pack(side=tk.RIGHT, padx=5)
        per_page_combo.bind('<<ComboboxSelected>>', self._on_per_page_change)

        # Таблица
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns_names = [col['name'] for col in self.columns_meta]
        self.tree = ttk.Treeview(table_frame, columns=columns_names,
                                 show='headings', selectmode='browse')

        v_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Стиль таблицы
        style = ttk.Style()
        style.configure("Treeview.Heading",
                        font=('Arial', 11, 'bold'),
                        anchor='center')
        style.configure("Treeview",
                        font=('Arial', 11),
                        rowheight=32)

        # Настройка колонок
        for col in self.columns_meta:
            col_name = col['name']
            label = col.get('label', col_name)
            col_width = col.get('width', 150)
            min_width = max(80, len(label) * 12 + 20)

            self.tree.heading(col_name,
                              text=label,
                              command=lambda c=col_name: self._sort_by_column(c))
            self.tree.column(col_name,
                             width=col_width,
                             minwidth=min_width,
                             anchor='center',
                             stretch=True)

        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)



        self.tree.bind('<<TreeviewSelect>>', self._on_tree_select)
        self.tree.bind('<Double-1>', self._on_double_click)


        nav_frame = ttk.Frame(self)
        nav_frame.pack(fill=tk.X, pady=(5, 0))

        self.first_btn = ttk.Button(nav_frame, text='<< Первая',
                                    command=self._go_first)
        self.first_btn.pack(side=tk.LEFT, padx=2)

        self.prev_btn = ttk.Button(nav_frame, text='< Пред',
                                   command=self._go_prev)
        self.prev_btn.pack(side=tk.LEFT, padx=2)

        self.page_label = tk.Label(nav_frame, text='Стр. 1 из 1',
                                   font=('Arial', 10), width=15)
        self.page_label.pack(side=tk.LEFT, padx=10)

        self.next_btn = ttk.Button(nav_frame, text='След >',
                                   command=self._go_next)
        self.next_btn.pack(side=tk.LEFT, padx=2)

        self.last_btn = ttk.Button(nav_frame, text='Последняя >>',
                                   command=self._go_last)
        self.last_btn.pack(side=tk.LEFT, padx=2)

        # Быстрый переход
        ttk.Label(nav_frame, text='Перейти:').pack(side=tk.RIGHT, padx=5)
        self.page_entry = ttk.Entry(nav_frame, width=5)
        self.page_entry.pack(side=tk.RIGHT, padx=2)
        self.page_entry.bind('<Return>', self._go_to_page)

        ttk.Button(nav_frame, text='→', width=3,
                   command=lambda: self._go_to_page(None)).pack(side=tk.RIGHT)


    #  ЗАГРУЗКА ДАННЫХ


    def load_page(self, page=None):
        """Загрузить указанную страницу с сервера."""
        if page is not None:
            self.current_page = page

        self.sort_column = None
        self.sort_reverse = False

        try:
            result = self.bl.get_all_paginated(
                self.table_name,
                page=self.current_page,
                per_page=self.per_page
            )

            self.raw_records = result['records']
            self.total_pages = result['total_pages']
            self.total_records = result['total']

            decorated = [DataFormatter.decorate_main_row(self.bl, row)
                         for row in self.raw_records]

            for item in self.tree.get_children():
                self.tree.delete(item)

            for idx, record in enumerate(decorated):
                values = [record.get(col['name'], '') for col in self.columns_meta]
                clean_values = [v if v is not None else '' for v in values]
                self.tree.insert('', tk.END, iid=str(idx), values=clean_values)


            self.info_label.config(
                text=f'Всего записей: {self.total_records} | '
                     f'Страница {self.current_page} из {self.total_pages}'
            )
            self.page_label.config(
                text=f'Стр. {self.current_page} из {self.total_pages}'
            )

            self._update_buttons()
            self._update_header_arrows()

        except Exception as e:
            self.info_label.config(text=f'Ошибка загрузки: {str(e)[:50]}...')

    #  СОРТИРОВКА

    def _sort_by_column(self, column):
        """Сортировка записей при клике на заголовок колонки."""

        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False  # первый клик всегда по возрастанию

        if self.raw_records:
            try:

                self.raw_records.sort(
                    key=lambda x: (
                        x.get(column) is None,
                        str(x.get(column, '')).lower() if x.get(column) is not None else ''
                    ),
                    reverse=self.sort_reverse
                )
            except Exception:
                pass


        self._redraw_current_page()
        self._update_header_arrows()

    def _redraw_current_page(self):
        """Перерисовать текущую страницу (без запроса к серверу)."""
        decorated = [DataFormatter.decorate_main_row(self.bl, row)
                     for row in self.raw_records]

        for item in self.tree.get_children():
            self.tree.delete(item)

        for idx, record in enumerate(decorated):
            values = [record.get(col['name'], '') for col in self.columns_meta]
            clean_values = [v if v is not None else '' for v in values]
            self.tree.insert('', tk.END, iid=str(idx), values=clean_values)

    def _update_header_arrows(self):
        """Обновить стрелочки ▲/▼ в заголовках колонок."""
        for col in self.columns_meta:
            col_name = col['name']
            label = col.get('label', col_name)

            if col_name == self.sort_column:
                arrow = ' ▼' if self.sort_reverse else ' ▲'
                self.tree.heading(col_name, text=label + arrow)
            else:
                self.tree.heading(col_name, text=label)


    #  НАВИГАЦИЯ ПО СТРАНИЦАМ

    def _update_buttons(self):
        """Обновить состояние кнопок навигации."""
        state_first = 'normal' if self.current_page > 1 else 'disabled'
        state_prev = 'normal' if self.current_page > 1 else 'disabled'
        state_next = 'normal' if self.current_page < self.total_pages else 'disabled'
        state_last = 'normal' if self.current_page < self.total_pages else 'disabled'

        self.first_btn.config(state=state_first)
        self.prev_btn.config(state=state_prev)
        self.next_btn.config(state=state_next)
        self.last_btn.config(state=state_last)

    def _go_first(self):
        """Перейти на первую страницу."""
        self.load_page(1)

    def _go_prev(self):
        """Перейти на предыдущую страницу."""
        if self.current_page > 1:
            self.load_page(self.current_page - 1)

    def _go_next(self):
        """Перейти на следующую страницу."""
        if self.current_page < self.total_pages:
            self.load_page(self.current_page + 1)

    def _go_last(self):
        """Перейти на последнюю страницу."""
        self.load_page(self.total_pages)

    def _go_to_page(self, event):
        """Перейти на страницу, введённую в поле."""
        try:
            page = int(self.page_entry.get())
            if 1 <= page <= self.total_pages:
                self.load_page(page)
            else:
                self.page_entry.delete(0, tk.END)
                self.page_entry.insert(0, str(self.current_page))
        except ValueError:
            pass

    def _on_per_page_change(self, event):
        """Обработчик изменения количества записей на странице."""
        self.per_page = int(self.per_page_var.get())
        self.current_page = 1
        self.load_page()


    #  ВЫДЕЛЕНИЕ И ДВОЙНОЙ КЛИК

    def _on_tree_select(self, event):
        """Обработчик выбора строки в таблице."""
        if self.on_select:
            selected = self.tree.selection()
            if selected:
                idx = int(selected[0])
                if 0 <= idx < len(self.raw_records):
                    self.on_select(self.raw_records[idx])

    def _on_double_click(self, event):
        """Обработчик двойного клика по строке."""
        if self.on_double_click:
            selected = self.get_selected()
            if selected:
                self.on_double_click(selected)

    def get_selected(self):
        """Возвращает выделенную запись (сырые данные) или None."""
        selected = self.tree.selection()
        if not selected:
            return None
        idx = int(selected[0])
        if 0 <= idx < len(self.raw_records):
            return self.raw_records[idx]
        return None



    def refresh(self):
        """Обновить текущую страницу (перезагрузить с сервера)."""
        self.load_page(self.current_page)