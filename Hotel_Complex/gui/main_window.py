import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

from gui.sizes import MAIN_WINDOW
from gui.utils import center_window


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'Core'))
sys.path.insert(0, os.path.join(BASE_DIR, 'Data_Acces'))

from Core.business import BusinessLogic
from Data_Acces.metadata import TABLES_META

from gui.edit_dialog import EditDialog
from gui.query_dialog import QueryDialog
from gui.special_forms import CheckinForm, CheckoutForm, CancelBookingForm, AddPaymentForm
from gui.utils import show_error, show_info, show_warning, ask_yes_no


class MainWindow:
    def __init__(self, role):
        self.role = role
        self.bl = BusinessLogic(role)
        self.current_table = None
        self.current_data = []
        self.tableView = None
        self.selected_record = None
        self.display_table_mapping = {}

        self.root = tk.Tk()
        self.root.title(f"Гостиничный комплекс - {self._role_name()}")

        width = MAIN_WINDOW['width']
        height = MAIN_WINDOW['height']
        self.root.geometry(f"{width}x{height}")
        center_window(self.root, width, height)

        self._create_menu()
        self._create_widgets()
        self._load_table_list()

    def _role_name(self):
        return self._get_role_display(self.role)

    def _get_role_display(self, role):
        return "Администратор" if role == 'admin' else "Менеджер"


    #  МЕНЮ


    def _create_menu(self):
        menubar = tk.Menu(self.root)


        ops_menu = tk.Menu(menubar, tearoff=0)
        ops_menu.add_command(label="🏨 Заселение", command=self._show_checkin_form)
        ops_menu.add_command(label="🚪 Выселение", command=self._show_checkout_form)
        ops_menu.add_command(label="❌ Отмена брони", command=self._show_cancel_booking_form)
        ops_menu.add_separator()
        ops_menu.add_command(label="💳 Добавить платёж", command=self._show_add_payment_form)
        menubar.add_cascade(label="Операции", menu=ops_menu)


        reports_menu = tk.Menu(menubar, tearoff=0)
        reports_menu.add_command(label="📊 Панель отчётов", command=self._show_reports_panel)
        menubar.add_cascade(label="Отчёты", menu=reports_menu)


        role_menu = tk.Menu(menubar, tearoff=0)
        role_menu.add_command(label="👤 Менеджер",
                              command=lambda: self._switch_role('manager'))
        role_menu.add_command(label="🔧 Администратор",
                              command=lambda: self._switch_role('admin'))
        menubar.add_cascade(label="Роль", menu=role_menu)


        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="О программе", command=self._show_about)
        menubar.add_cascade(label="Справка", menu=help_menu)

        self.root.config(menu=menubar)

    def _switch_role(self, new_role):
        """Сменить роль в текущей сессии."""
        if new_role == self.role:
            show_info(self.root, f"Вы уже работаете как {self._role_name()}")
            return

        if not ask_yes_no(self.root,
                          f"Сменить роль на «{self._get_role_display(new_role)}»?\n\n"
                          f"Текущая сессия будет обновлена.\n"
                          f"Несохранённые изменения будут потеряны."):
            return

        self.role = new_role
        self.bl = BusinessLogic(new_role)
        self.root.title(f"Гостиничный комплекс - {self._role_name()}")
        self.current_table = None
        self.selected_record = None
        self._load_table_list()

        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.tableView = None
        self._update_buttons_state()

        show_info(self.root, f"Роль изменена на «{self._get_role_display(new_role)}»")


    #  WIDGETS


    def _create_widgets(self):
        # Левая панель - список таблиц
        left_frame = ttk.Frame(self.root, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_frame.pack_propagate(False)  # ← КРИТИЧНО: не даём сжаться

        tk.Label(left_frame, text="Таблицы", font=('Arial', 12, 'bold')).pack(pady=(5, 0))

        # Listbox с рамкой
        list_frame = tk.Frame(left_frame, bd=2, relief='sunken')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.table_listbox = tk.Listbox(list_frame, font=('Arial', 10))
        self.table_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.table_listbox.bind('<<ListboxSelect>>', self._on_table_select)


        #self.table_listbox.insert(tk.END, " ТАБЛИЦЫ ЗДЕСЬ ")


        right_frame = ttk.Frame(self.root)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)


        toolbar = ttk.Frame(right_frame)
        toolbar.pack(fill=tk.X, pady=5)

        self.view_btn = ttk.Button(toolbar, text="🔍 Просмотр", command=self._view_record)
        self.view_btn.pack(side=tk.LEFT, padx=5)

        self.add_btn = ttk.Button(toolbar, text="➕ Добавить", command=self._add_record)
        self.add_btn.pack(side=tk.LEFT, padx=5)

        self.edit_btn = ttk.Button(toolbar, text="✏ Редактировать", command=self._edit_record)
        self.edit_btn.pack(side=tk.LEFT, padx=5)

        self.delete_btn = ttk.Button(toolbar, text="🗑 Удалить", command=self._delete_record)
        self.delete_btn.pack(side=tk.LEFT, padx=5)

        self.refresh_btn = ttk.Button(toolbar, text="🔄 Обновить", command=self._refresh_table)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        self.reports_btn = ttk.Button(toolbar, text="📊 Отчёты", command=self._show_reports_panel)
        self.reports_btn.pack(side=tk.LEFT, padx=(20, 5))

        # Фрейм для таблицы
        self.table_frame = ttk.Frame(right_frame)
        self.table_frame.pack(fill=tk.BOTH, expand=True)


    #  ЗАГРУЗКА ТАБЛИЦ

    def _load_table_list(self):
        """Загружает полный список таблиц ИС."""
        from Core.role_permissions import get_table_list

        if self.role == 'admin':
            allowed_raw_tables = set(TABLES_META.keys())
        else:
            allowed_raw_tables = get_table_list(self.role, 'read') or set()

        # Покажем, что реально в allowed_raw_tables
        print(f"[DEBUG] allowed_raw_tables: {sorted(allowed_raw_tables)[:5]}...")

        self.table_listbox.delete(0, tk.END)
        self.display_table_mapping = {}

        # Простой список без проверок — добавляем ВСЁ
        tables = [
            ('👥 Клиенты', 'client'),
            ('📅 Бронирования', 'booking'),
            ('🏨 Проживания', 'stay'),
            ('🛏 Номерной фонд', 'room'),
            ('💵 Тарифы', 'room_tariff'),
            ('🏢 Корпуса', 'building'),
            ('🛠 Услуги', 'service_type'),
            ('📊 Использование услуг', 'service_usage'),
            ('🧾 Счета', 'invoice'),
            ('💳 Платежи', 'payment'),
            ('⚠️ Жалобы', 'complaint'),
            ('⭐ Отзывы', 'review'),
            ('🏢 Организации', 'organization'),
            ('📜 Договоры', 'contract'),
            ('🔗 Бронь-Номера', 'booking_room'),
            ('🔗 Бронь-Клиенты', 'booking_client'),
            ('🔗 Проживание-Клиенты', 'stay_client'),
            ('🔗 Корпус-Услуги', 'building_service'),
            ('⚙️ Типы корпусов', 'building_type'),
            ('⚙️ Типы организаций', 'organization_type'),
            ('⚙️ Категории комнат', 'room_type'),
            ('🏢 Турфирмы', 'organization_tour_agency'),
            ('🎤 Организаторы', 'organization_event_organizer'),
            ('⚠️ Штрафы', 'penalty'),
            ('💰 Фин. штрафы', 'financial_penalty'),
            ('📉 Расходы', 'expense'),
        ]

        count = 0
        for user_label, raw_name in tables:
            if raw_name in allowed_raw_tables:
                self.table_listbox.insert(tk.END, user_label)
                self.display_table_mapping[user_label] = raw_name
                count += 1
            else:
                print(f"[DEBUG] SKIPPED: {raw_name} (not in allowed)")

        print(f"[DEBUG] Inserted {count} items into listbox")
        print(f"[DEBUG] Listbox size after: {self.table_listbox.size()}")

        self._update_buttons_state()

    def _update_buttons_state(self):
        if not self.current_table:
            self.add_btn.config(state='disabled')
            self.edit_btn.config(state='disabled')
            self.delete_btn.config(state='disabled')
            self.view_btn.config(state='disabled')
            return

        can_write = self.bl.can_write(self.current_table)
        can_delete = self.bl.can_delete(self.current_table)

        self.add_btn.config(state='normal' if can_write else 'disabled')
        self.edit_btn.config(state='normal' if can_write else 'disabled')
        self.delete_btn.config(state='normal' if can_delete else 'disabled')
        self.view_btn.config(state='normal')

    def _on_table_select(self, event):
        selection = self.table_listbox.curselection()
        if not selection:
            return

        selected_label = self.table_listbox.get(selection[0])
        table_name = self.display_table_mapping.get(selected_label)

        if table_name:
            self.current_table = table_name
            self._update_buttons_state()
            self._refresh_table()

    #  ТАБЛИЦА ДАННЫХ

    def _refresh_table(self):
        if not self.current_table:
            return

        try:
            from gui.paginated_table_view import PaginatedTableView

            for widget in self.table_frame.winfo_children():
                widget.destroy()

            meta = TABLES_META.get(self.current_table)
            if not meta:
                show_error(self.root, f"Нет метаданных для {self.current_table}")
                return

            pk_name = meta.get('pk')
            columns = []

            for field in meta['fields']:
                if field['name'] == pk_name:
                    continue


                field_name = field['name']
                field_type = field['type']
                field_label = field['label']

                width = 140

                if 'name' in field_name or 'title' in field_name:
                    width = 220
                elif 'description' in field_name:
                    width = 280
                elif 'text' in field_name or 'resolution' in field_name:
                    width = 300
                elif 'reason' in field_name:
                    width = 280
                elif 'address' in field_name:
                    width = 220
                elif 'email' in field_name:
                    width = 220
                elif 'phone' in field_name:
                    width = 170
                elif 'passport' in field_name or 'license' in field_name:
                    width = 180
                elif 'number' in field_name:
                    width = 200
                elif 'id' in field_name:
                    width = 120
                elif field_type == 'timestamp':
                    width = 170
                elif field_type == 'date':
                    width = 130
                elif field_type == 'bool':
                    width = 110
                elif field_type == 'numeric':
                    width = 150
                elif field_type == 'fk':
                    width = 220
                elif field_type == 'text':
                    width = 300


                label_len = len(field_label)
                min_by_label = label_len * 11 + 20
                if min_by_label > width:
                    width = min_by_label


                if width > 350:
                    width = 350

                columns.append({
                    'name': field_name,
                    'label': field_label,
                    'width': width
                })


            self.tableView = PaginatedTableView(
                self.table_frame,
                self.bl,
                self.current_table,
                columns,
                per_page=50,
                on_select=self._on_record_select,
                on_double_click=lambda rec: self._view_record()
            )
            self.tableView.pack(fill=tk.BOTH, expand=True)
            self.tableView.load_page(1)

        except Exception as e:
            show_error(self.root, f"Ошибка загрузки данных: {e}")

    def _on_record_select(self, record):
        self.selected_record = record

    def _view_record(self):
        if not self.current_table or not hasattr(self, 'tableView') or self.tableView is None:
            show_warning(self.root, "Сначала выберите таблицу")
            return

        selected = self.tableView.get_selected()
        if not selected:
            show_warning(self.root, "Выберите запись для просмотра")
            return

        from gui.detail_view import DetailView
        DetailView(self.root, self.bl, self.current_table, selected)


    #  CRUD

    def _add_record(self):
        if not self.current_table:
            return
        EditDialog(self.root, self.bl, self.current_table, record=None, on_save=self._refresh_table)

    def _edit_record(self):
        if not self.current_table or not hasattr(self, 'tableView') or self.tableView is None:
            return

        selected = self.tableView.get_selected()
        if not selected:
            show_warning(self.root, "Выберите запись для редактирования")
            return

        EditDialog(self.root, self.bl, self.current_table, record=selected, on_save=self._refresh_table)

    def _delete_record(self):
        if not hasattr(self, 'tableView') or self.tableView is None:
            return

        self.selected_record = self.tableView.get_selected()

        if not self.selected_record:
            show_warning(self.root, "Выберите запись для удаления")
            return

        meta = TABLES_META.get(self.current_table, {})
        pk_name = meta.get('pk')
        if not pk_name:
            show_error(self.root, "Для этой таблицы удаление не поддерживается")
            return

        pk_value = self.selected_record.get(pk_name)

        if ask_yes_no(self.root, "Удалить выбранную запись?"):
            try:
                self.bl.delete(self.current_table, pk_name, pk_value)
                self._refresh_table()
                show_info(self.root, "Запись успешно удалена")
                self.selected_record = None
            except Exception as e:
                show_error(self.root, f"Ошибка удаления: {e}")


    #  ОТЧЁТЫ И ОПЕРАЦИИ


    def _show_reports_panel(self):
        from gui.reports_panel import ReportsPanel
        ReportsPanel(self.root, self.bl)

    def _run_report(self, report_id):
        QueryDialog(self.root, self.bl, report_id)

    def _show_checkin_form(self):
        CheckinForm(self.root, self.bl, on_success=self._refresh_table)

    def _show_checkout_form(self):
        CheckoutForm(self.root, self.bl, on_success=self._refresh_table)

    def _show_cancel_booking_form(self):
        CancelBookingForm(self.root, self.bl, on_success=self._refresh_table)

    def _show_add_payment_form(self):
        AddPaymentForm(self.root, self.bl, on_success=self._refresh_table)

    def _show_about(self):
        messagebox.showinfo("О программе",
                            "Гостиничный комплекс\n"
                            
                            "Разработано для курса 'Базы данных'\n"
                            "Автор: Лунькова Екатерина 23210",
                            parent=self.root)

    def run(self):
        self.root.mainloop()