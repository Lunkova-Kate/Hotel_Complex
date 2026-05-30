# gui/table_view.py
import tkinter as tk
from tkinter import ttk

class TableView(ttk.Frame):
    """Компонент отображения данных, инкапсулирующий работу с Treeview."""

    def __init__(self, parent, columns, on_select=None):
        super().__init__(parent)
        self.columns = columns
        self.on_select = on_select
        self.raw_records = []
        self.tree = None
        self._create_tree()

    def _create_tree(self):
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True)

        columns_names = [col['name'] for col in self.columns]
        self.tree = ttk.Treeview(frame, columns=columns_names, show='headings', selectmode='browse')

        v_scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scroll = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)


        style = ttk.Style()


        style.configure("Treeview.Heading",
                        font=('Arial', 11, 'bold'),
                        anchor='center')


        style.configure("Treeview",
                        font=('Arial', 11),
                        rowheight=32)


        self.tree.tag_configure('evenrow', background='#f5f7fa')
        self.tree.tag_configure('oddrow', background='#ffffff')


        for col in self.columns:
            col_name = col['name']
            col_width = col.get('width', 150)
            min_width = self._calculate_min_width(col)

            self.tree.heading(col_name, text=col['label'])
            self.tree.column(col_name,
                             width=col_width,
                             minwidth=min_width,  # Минимальная ширина — защита от сжатия
                             anchor='center',  # Текст по центру ячейки
                             stretch=True)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.bind('<<TreeviewSelect>>', self._on_tree_select)

    def _calculate_min_width(self, col):

        label = col.get('label', col['name'])

        min_width = len(label) * 12 + 20

        return max(80, min(min_width, 200))

    def _on_tree_select(self, event):
        if self.on_select:
            selected = self.tree.selection()
            if selected:
                idx = int(selected[0])
                if 0 <= idx < len(self.raw_records):

                    self.on_select(self.raw_records[idx])

    def populate(self, raw_data, decorated_data):

        self.raw_records = raw_data
        for item in self.tree.get_children():
            self.tree.delete(item)

        for idx, record in enumerate(decorated_data):
            values = [record.get(col['name'], '') for col in self.columns]
            clean_values = [v if v is not None else '' for v in values]
            # iid строки связываем строго с её индексом в массиве raw_records
            self.tree.insert('', tk.END, iid=str(idx), values=clean_values)

    def get_selected(self):

        selected = self.tree.selection()
        if not selected:
            return None
        idx = int(selected[0])
        if 0 <= idx < len(self.raw_records):
            return self.raw_records[idx]
        return None