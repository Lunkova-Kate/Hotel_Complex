import tkinter as tk
from tkinter import ttk
from gui.sizes import DETAIL_VIEW
from gui.utils import center_window
from gui.constants import (
    STATUS_LABELS,
    DETAIL_VIEW_TABLE_NAMES,
    DATE_DISPLAY_FORMAT,
    TIMESTAMP_DISPLAY_FORMAT
)
from Data_Acces.metadata import TABLES_META


class DetailView:
    """Окно детального просмотра одной записи в формате карточки."""

    def __init__(self, parent, business_logic, table_name, record):

        self.parent = parent
        self.bl = business_logic
        self.table_name = table_name
        self.record = record

        self.meta = TABLES_META.get(table_name)
        if not self.meta:
            from tkinter import messagebox
            messagebox.showerror("Ошибка", f"Нет метаданных для таблицы {table_name}")
            return

        self.window = tk.Toplevel(parent)
        self.window.title(f"Просмотр записи — {self._get_table_display_name()}")
        self.window.resizable(True, True)


        width = DETAIL_VIEW['width']
        height = min(DETAIL_VIEW['height'], 80 + len(self.meta['fields']) * 38)
        self.window.geometry(f"{width}x{height}")
        center_window(self.window, width, height)

        self.window.transient(parent)
        self.window.grab_set()

        self._create_widgets()

        self._bind_mousewheel()

    def _get_table_display_name(self):
        return DETAIL_VIEW_TABLE_NAMES.get(self.table_name, self.table_name)

    def _create_widgets(self):

        outer_frame = ttk.Frame(self.window)
        outer_frame.pack(fill=tk.BOTH, expand=True)


        header_frame = ttk.Frame(outer_frame, padding="15")
        header_frame.pack(fill=tk.X)

        pk_name = self.meta.get('pk')
        pk_value = self.record.get(pk_name, '—') if pk_name else '—'

        title = f"{self._get_table_display_name()} #{pk_value}"
        tk.Label(header_frame, text=title, font=('Arial', 16, 'bold'),
                 fg='#2c3e50').pack(anchor='w')


        ttk.Separator(outer_frame, orient='horizontal').pack(fill='x', padx=10)

        canvas_frame = ttk.Frame(outer_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw",
                                  tags="scrollable_frame")
        self.canvas.configure(yscrollcommand=scrollbar.set)


        self.canvas.bind('<Configure>', self._on_canvas_configure)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._populate_fields()

        btn_frame = ttk.Frame(outer_frame, padding="10")
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="Закрыть", command=self.window.destroy,
                   width=15).pack(side=tk.RIGHT, padx=10)

    def _on_canvas_configure(self, event):
        """Подгоняем ширину внутреннего фрейма под ширину канваса."""
        self.canvas.itemconfig("scrollable_frame", width=event.width)

    def _bind_mousewheel(self):
        """Привязка колесика мыши к прокрутке."""

        def on_mousewheel(event):
            # Для Windows
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def on_mousewheel_linux(event):
            # Для Linux
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")


        self.canvas.bind_all("<MouseWheel>", on_mousewheel)

        self.canvas.bind_all("<Button-4>", on_mousewheel_linux)
        self.canvas.bind_all("<Button-5>", on_mousewheel_linux)


        def unbind_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")

        self.window.bind("<Destroy>", unbind_mousewheel)

    def _populate_fields(self):
        """Заполнить поля карточки."""
        row = 0

        for field in self.meta['fields']:
            field_name = field['name']
            field_label = field['label']
            field_type = field['type']

            raw_value = self.record.get(field_name)


            display_value = self._format_value(field_name, field_type, raw_value)


            bg_color = '#f8f9fa' if row % 2 == 0 else '#ffffff'

            # Фрейм для одной строки
            row_frame = tk.Frame(self.scrollable_frame, bg=bg_color,
                                 highlightbackground='#e9ecef',
                                 highlightthickness=1)
            row_frame.pack(fill='x', padx=15, pady=1)


            label_text = f"{field_label}:"
            label_widget = tk.Label(row_frame, text=label_text,
                                    font=('Arial', 10, 'bold'),
                                    bg=bg_color, fg='#495057',
                                    anchor='e', width=28)
            label_widget.pack(side=tk.LEFT, padx=(15, 10), pady=8)


            value_widget = tk.Label(row_frame, text=display_value,
                                    font=('Arial', 10),
                                    bg=bg_color, fg='#212529',
                                    anchor='w', justify='left',
                                    wraplength=400)
            value_widget.pack(side=tk.LEFT, padx=(0, 15), pady=8, fill='x', expand=True)

            row += 1


        if row == 0:
            tk.Label(self.scrollable_frame, text="Нет данных для отображения",
                     font=('Arial', 12, 'italic'), fg='gray').pack(pady=30)

    def _format_value(self, field_name, field_type, raw_value):
        """Форматировать значение для отображения в карточке."""

        # None / пусто
        if raw_value is None:
            return '—'

        # Булевы значения
        if field_type == 'bool':
            return 'Да' if raw_value else 'Нет'

        # Статусы и методы оплаты
        if field_name in ['status', 'method']:
            return STATUS_LABELS.get(raw_value, str(raw_value))

        # Внешние ключи — получаем читаемое имя
        if field_type == 'fk':
            return self._resolve_fk(field_name, raw_value)

        # Даты —  форматирование
        if field_type == 'date':
            if hasattr(raw_value, 'strftime'):
                return raw_value.strftime(DATE_DISPLAY_FORMAT)
            return str(raw_value)[:10]

        if field_type == 'timestamp':
            if hasattr(raw_value, 'strftime'):
                return raw_value.strftime(TIMESTAMP_DISPLAY_FORMAT)
            return str(raw_value)[:16]

        # Числа
        if field_type in ('int', 'numeric'):
            if isinstance(raw_value, float):
                return f"{raw_value:,.2f}".replace(',', ' ')
            return str(raw_value)

        # Текст
        return str(raw_value)


    def _resolve_fk(self, field_name, fk_value):
        """Разрешить внешний ключ в читаемое имя."""

        fk_mapping = {
            'building_type_id': ('building_type', 'name'),
            'building_id': ('building', 'name'),
            'room_type_id': ('room_type', 'name'),
            'room_id': ('room', 'room_number'),
            'service_type_id': ('service_type', 'name'),
            'organization_type_id': ('organization_type', 'name'),
            'organization_id': ('organization', 'name'),
            'contract_id': ('contract', 'contract_number'),
            'client_id': ('client', 'last_name'),
            'booking_id': ('booking', 'booking_id'),
            'stay_id': ('stay', 'stay_id'),
            'invoice_id': ('invoice', 'invoice_id'),
            'tariff_id': ('room_tariff', 'tariff_id'),
            'payment_id': ('payment', 'payment_id'),
            'complaint_id': ('complaint', 'complaint_id'),
            'review_id': ('review', 'review_id'),
            'expense_id': ('expense', 'expense_id'),
            'penalty_id': ('penalty', 'penalty_id'),
        }

        if field_name not in fk_mapping:
            return str(fk_value)

        ref_table, display_col = fk_mapping[field_name]

        try:

            record = self.bl.get_by_id(ref_table, f"{ref_table}_id", fk_value)
            if record:

                if ref_table == 'client':
                    last = record.get('last_name', '')
                    first = record.get('first_name', '')
                    return f"{last} {first[:1]}." if first else last


                if ref_table == 'room':
                    return f"№{record.get('room_number', fk_value)}"


                if ref_table == 'contract':
                    return f"Договор №{record.get('contract_number', fk_value)}"

                return str(record.get(display_col, fk_value))
        except Exception:
            pass

        return f"#{fk_value}"