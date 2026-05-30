# gui/edit_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from gui.sizes import EDIT_DIALOG
from gui.utils import center_window
from gui.formatter import DataFormatter


class EditDialog:
    """Диалог добавления/редактирования с защитой ID полей."""

    def __init__(self, parent, business_logic, table_name, record=None, on_save=None):
        self.parent = parent
        self.bl = business_logic
        self.table_name = table_name
        self.record = record
        self.on_save = on_save
        self.entries = {}
        self.fk_combos = {}
        self.placeholders = {}

        from Data_Acces.metadata import TABLES_META
        self.meta = TABLES_META.get(table_name)
        if not self.meta:
            messagebox.showerror("Ошибка", f"Нет метаданных для таблицы {table_name}", parent=parent)
            return

        self.window = tk.Toplevel(parent)
        title = f"Редактирование записи" if record else f"Добавление новой записи"
        self.window.title(title)
        self.window.resizable(True, True)  # Разрешаем ресайз для длинных форм

        width = EDIT_DIALOG['width']
        height = EDIT_DIALOG['height']
        self.window.geometry(f"{width}x{height}")
        center_window(self.window, width, height)
        self.window.transient(parent)
        self.window.grab_set()

        self._create_widgets()

    def _setup_placeholder(self, entry, field_name, placeholder_text):
        """Внедряет умный текстовый плейсхолдер в поле Entry."""
        self.placeholders[field_name] = placeholder_text

        if not self.record:
            entry.insert(0, placeholder_text)
            entry.config(fg='gray')

        def on_focus_in(event):
            if entry.get() == placeholder_text:
                entry.delete(0, tk.END)
                entry.config(fg='black')

        def on_focus_out(event):
            if not entry.get().strip():
                entry.insert(0, placeholder_text)
                entry.config(fg='gray')

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def _create_readonly_field(self, parent, row, label_text, value):
        """Создает нередактируемое поле с серым фоном."""
        tk.Label(parent, text=label_text, anchor='e', font=('Arial', 10)).grid(
            row=row, column=0, sticky='e', padx=10, pady=5
        )

        display_value = str(value) if value is not None else '—'

        value_frame = tk.Frame(parent, bg='#f0f0f0', relief='sunken', bd=1)
        value_frame.grid(row=row, column=1, sticky='w', padx=10, pady=5)

        tk.Label(value_frame, text=display_value,
                 font=('Arial', 10, 'bold'), fg='#555555',
                 bg='#f0f0f0', padx=10, pady=3).pack()

        tk.Label(parent, text="(не редактируется)",
                 font=('Arial', 8), fg='gray').grid(row=row, column=2, padx=5)

    def _create_widgets(self):
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Привязка колесика мыши
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)
        self.window.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

        row = 0
        pk_name = self.meta.get('pk')

        for field in self.meta['fields']:
            field_name = field['name']
            field_label = field['label']
            field_type = field['type']
            editable = field.get('editable', True)
            required = field.get('required', False)
            is_pk = field.get('is_pk', False)

            # Определяем текущее значение
            current_value = self.record.get(field_name) if self.record else None

            # ===== ПОЛЯ ID (первичные ключи) =====
            # При создании новой записи - пропускаем (БД сама сгенерирует)
            # При редактировании - показываем, но не даём менять
            if is_pk or field_name == pk_name:
                if self.record:  # Только при редактировании показываем ID
                    self._create_readonly_field(scrollable_frame, row, f"{field_label}:", current_value)
                    row += 1
                continue  # При создании пропускаем ID полностью

            # ===== НЕРЕДАКТИРУЕМЫЕ ПОЛЯ (created_at, calculated и т.д.) =====
            if not editable and self.record:
                self._create_readonly_field(scrollable_frame, row, f"{field_label}:", current_value)
                row += 1
                continue

            # ===== РЕДАКТИРУЕМЫЕ ПОЛЯ =====
            label_text = f"{field_label}{'*' if required else ':'}"
            tk.Label(scrollable_frame, text=label_text, anchor='e', font=('Arial', 10)).grid(
                row=row, column=0, sticky='e', padx=10, pady=5
            )

            # FK поля
            if field_type == 'fk':
                ref_table = field['ref_table']
                display_col = field['display_col']

                if ref_table == 'client':
                    display_col = 'last_name'
                elif ref_table == 'room':
                    display_col = 'room_number'

                try:
                    options = self.bl.get_fk_options(ref_table, display_col)
                    mapping = {}
                    combo_values = []

                    if not required:
                        mapping["[ Не выбрано ]"] = None
                        combo_values.append("[ Не выбрано ]")

                    for opt in options:
                        o_id, o_val = opt[0], opt[1]
                        if ref_table == 'client':
                            label = f"Клиент: {o_val}"
                        elif ref_table == 'room':
                            label = f"Комната № {o_val}"
                        elif ref_table == 'building':
                            label = f"Корпус: {o_val}"
                        elif ref_table == 'contract':
                            label = f"Договор № {o_val}"
                        else:
                            label = f"{o_val}"

                        mapping[label] = o_id
                        combo_values.append(label)

                    combo = ttk.Combobox(scrollable_frame, values=combo_values, state="readonly", width=40)
                    combo.grid(row=row, column=1, padx=10, pady=5, sticky='w')

                    combo.user_mapping = mapping
                    self.fk_combos[field_name] = combo

                    if current_value is not None:
                        for label, idx in mapping.items():
                            if idx == current_value:
                                combo.set(label)
                                break
                    else:
                        if not required and combo_values:
                            combo.set(combo_values[0])

                except Exception as e:
                    tk.Label(scrollable_frame, text=f"Ошибка загрузки: {e}", fg='red').grid(
                        row=row, column=1, padx=10, pady=5)

            # Поля с choices (статусы, методы)
            elif 'choices' in field or field_name in ['status', 'method']:
                if field_name == 'status' and self.table_name == 'booking':
                    choices_list = ['🟢 Активна', '🔴 Отменена', '🏨 Заселена (Выполнена)', '⚠️ Гость не явился']
                elif field_name == 'status' and self.table_name == 'invoice':
                    choices_list = ['🧾 Открыт (Не оплачен)', '💳 Оплачен частично', '✅ Оплачен полностью',
                                    '❌ Аннулирован']
                elif field_name == 'status' and self.table_name == 'complaint':
                    choices_list = ['🆕 Новая', '⚙️ В работе', '🔒 Закрыта']
                elif field_name == 'method':
                    choices_list = ['💵 Наличные', '💳 Банковская карта', '🏦 Банковский перевод', '📁 Другое']
                else:
                    choices_list = field.get('choices', [])

                combo = ttk.Combobox(scrollable_frame, values=choices_list, state="readonly", width=40)
                combo.grid(row=row, column=1, padx=10, pady=5, sticky='w')
                self.entries[field_name] = combo

                if current_value is not None:
                    for ru_label in choices_list:
                        clean_eng = (ru_label.replace('🟢 ', '').replace('🔴 ', '').replace('🏨 ', '')
                                     .replace('⚠️ ', '').replace('🧾 ', '').replace('💳 ', '')
                                     .replace('✅ ', '').replace('❌ ', '').replace('🆕 ', '')
                                     .replace('⚙️ ', '').replace('🔒 ', '').replace('💵 ', '')
                                     .replace('🏦 ', '').replace('📁 ', ''))
                        if (current_value in ru_label or clean_eng in current_value or
                                (current_value == 'FULFILLED' and 'Заселена' in ru_label)):
                            combo.set(ru_label)
                            break
                else:
                    if combo['values']:
                        combo.current(0)

            # Boolean поля
            elif field_type == 'bool':
                combo = ttk.Combobox(scrollable_frame, values=['Да', 'Нет'], state="readonly", width=40)
                combo.grid(row=row, column=1, padx=10, pady=5, sticky='w')
                self.entries[field_name] = combo

                if current_value is not None:
                    combo.set('Да' if current_value else 'Нет')
                else:
                    combo.set('Нет')

            # Text поля
            elif field_type == 'text':
                text_widget = tk.Text(scrollable_frame, width=40, height=5)
                text_widget.grid(row=row, column=1, padx=10, pady=5, sticky='w')
                if current_value:
                    text_widget.insert('1.0', current_value)
                self.entries[field_name] = text_widget

            # Обычные поля ввода
            else:
                entry = tk.Entry(scrollable_frame, width=43, bd=1, relief='sunken')
                entry.grid(row=row, column=1, padx=10, pady=5, sticky='w')
                self.entries[field_name] = entry

                if current_value is not None:
                    if isinstance(current_value, datetime):
                        fmt = '%Y-%m-%d %H:%M:%S' if field_type == 'timestamp' else '%Y-%m-%d'
                        entry.insert(0, current_value.strftime(fmt))
                    else:
                        entry.insert(0, str(current_value))
                else:
                    if field_type in DataFormatter.FIELD_PLACEHOLDERS:
                        self._setup_placeholder(entry, field_name, DataFormatter.FIELD_PLACEHOLDERS[field_type])
                    elif field_name in DataFormatter.FIELD_PLACEHOLDERS:
                        self._setup_placeholder(entry, field_name, DataFormatter.FIELD_PLACEHOLDERS[field_name])

            # Подсказки
            if 'maxlen' in field:
                hint = f" (макс. {field['maxlen']} симв.)"
                tk.Label(scrollable_frame, text=hint, font=('Arial', 8)).grid(row=row, column=2, padx=5)

            row += 1

        # Кнопки
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=20)

        ttk.Button(btn_frame, text="Сохранить", command=self._save, width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self.window.destroy, width=15).pack(side=tk.LEFT, padx=10)

    def _get_value(self, field_name, entry, field_type):
        """Получить значение из виджета с обратным переводом в системные типы БД."""
        if field_type == 'fk':
            combo = self.fk_combos.get(field_name)
            selected_text = combo.get()
            return combo.user_mapping.get(selected_text) if selected_text else None

        if field_type == 'bool' and isinstance(entry, ttk.Combobox):
            return True if entry.get() == 'Да' else False

        if isinstance(entry, ttk.Combobox) and field_name in ['status', 'method']:
            val = entry.get()
            if 'Активна' in val: return 'ACTIVE'
            if 'Отменена' in val: return 'CANCELLED'
            if 'Заселена' in val: return 'FULFILLED'
            if 'Неявка' in val: return 'NO_SHOW'
            if 'Открыт' in val: return 'OPEN'
            if 'Частично' in val: return 'PARTIALLY_PAID'
            if 'полностью' in val: return 'PAID'
            if 'Аннулирован' in val: return 'CANCELLED'
            if 'Новая' in val: return 'NEW'
            if 'В работе' in val: return 'IN_PROGRESS'
            if 'Закрыта' in val: return 'CLOSED'
            if 'Наличные' in val: return 'CASH'
            if 'Карта' in val: return 'CARD'
            if 'Перевод' in val: return 'TRANSFER'
            if 'Другое' in val: return 'OTHER'
            return val

        if field_type == 'text':
            value = entry.get('1.0', 'end-1c').strip()
            return value if value else None

        value = entry.get().strip()
        if field_name in self.placeholders and value == self.placeholders[field_name]:
            return None

        if not value:
            return None

        if field_type in ('int', 'numeric'):
            try:
                return int(value) if field_type == 'int' else float(value)
            except ValueError:
                return value

        return value

    def _save(self):
        """Сбор данных и отправка в бэкенд с защитой от изменения ID."""
        try:
            data = {}
            pk_name = self.meta.get('pk')
            pk_value = None

            if self.record and pk_name:
                pk_value = self.record.get(pk_name)

            for field in self.meta['fields']:
                field_name = field['name']
                field_type = field['type']
                editable = field.get('editable', True)
                required = field.get('required', False)
                is_pk = field.get('is_pk', False)

                # ПРОПУСКАЕМ ВСЕ ID ПОЛЯ
                if is_pk or field_name == pk_name:
                    continue

                # Пропускаем нередактируемые поля при редактировании
                if not editable and self.record:
                    continue

                # Получаем виджет
                if field_type == 'fk':
                    entry = self.fk_combos.get(field_name)
                else:
                    entry = self.entries.get(field_name)

                if entry is None:
                    continue

                value = self._get_value(field_name, entry, field_type)

                # Валидация обязательных полей
                if required and (value is None or value == ''):
                    raise ValueError(f"Поле '{field['label']}' обязательно для заполнения")

                # Валидация числовых ограничений
                if value is not None and value != '':
                    if 'min' in field:
                        try:
                            num_val = float(value) if isinstance(value, str) else value
                            if num_val < field['min']:
                                raise ValueError(f"Поле '{field['label']}' должно быть не меньше {field['min']}")
                        except (TypeError, ValueError):
                            pass

                    if 'max' in field:
                        try:
                            num_val = float(value) if isinstance(value, str) else value
                            if num_val > field['max']:
                                raise ValueError(f"Поле '{field['label']}' должно быть не больше {field['max']}")
                        except (TypeError, ValueError):
                            pass

                    if 'maxlen' in field and isinstance(value, str) and len(value) > field['maxlen']:
                        raise ValueError(f"Поле '{field['label']}' не должно превышать {field['maxlen']} символов")

                # Добавляем только не-None значения
                if value is not None:
                    data[field_name] = value

            # Отправляем данные
            if self.record and pk_value is not None:
                # Убеждаемся, что в data нет pk
                if pk_name in data:
                    del data[pk_name]
                self.bl.update(self.table_name, pk_name, pk_value, data)
                messagebox.showinfo("Успех", "Запись успешно обновлена!", parent=self.window)
            else:
                self.bl.insert(self.table_name, data)
                messagebox.showinfo("Успех", "Новая запись успешно добавлена!", parent=self.window)

            self.window.destroy()
            if self.on_save:
                self.on_save()

        except ValueError as e:
            messagebox.showerror("Ошибка ввода данных", str(e), parent=self.window)

        except Exception as e:
            error_msg = str(e)

            friendly_messages = {
                'Этаж номера превышает количество этажей корпуса':
                    'Номер комнаты не может быть размещен на этаже, которого нет в выбранном корпусе.\n'
                    'Проверьте соответствие этажа и корпуса.',
                'Количество проживающих превышает вместимость номера':
                    'Нельзя заселить больше гостей, чем позволяет вместимость выбранного типа номера.\n'
                    'Выберите номер с большей вместимостью или сократите количество проживающих.',
                'duplicate key':
                    'Запись с такими данными уже существует в системе.\n'
                    'Проверьте уникальные поля (например, паспортные данные, телефон, email).',
                'violates foreign key constraint':
                    'Невозможно выполнить операцию: есть связанные данные в других таблицах.\n'
                    'Сначала удалите или измените связанные записи.',
                'violates not-null constraint':
                    'Одно из обязательных полей не заполнено.\n'
                    'Проверьте все поля, отмеченные звёздочкой (*).',
                'value too long':
                    'Введенное значение превышает допустимую длину.\n'
                    'Сократите текст в соответствующем поле.',
            }

            friendly_message = None
            for pattern, message in friendly_messages.items():
                if pattern.lower() in error_msg.lower():
                    friendly_message = message
                    break

            if friendly_message:
                messagebox.showerror("Ошибка сохранения", friendly_message, parent=self.window)
            else:
                messagebox.showerror(
                    "Ошибка базы данных",
                    f"Произошла ошибка при сохранении данных.\n\n"
                    f"Техническая информация:\n{error_msg.split('CONTEXT:')[0].strip()}",
                    parent=self.window
                )