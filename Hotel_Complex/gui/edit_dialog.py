# gui/edit_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from gui.sizes import EDIT_DIALOG
from gui.utils import center_window
from gui.formatter import DataFormatter


class EditDialog:
    """Диалог добавления/редактирования с поддержкой плейсхолдеров форматов ввода."""

    def __init__(self, parent, business_logic, table_name, record=None, on_save=None):
        self.parent = parent
        self.bl = business_logic
        self.table_name = table_name
        self.record = record
        self.on_save = on_save
        self.entries = {}
        self.fk_combos = {}
        self.placeholders = {}

        from metadata import TABLES_META
        self.meta = TABLES_META.get(table_name)
        if not self.meta:
            messagebox.showerror("Ошибка", f"Нет метаданных для таблицы {table_name}", parent=parent)
            return

        self.window = tk.Toplevel(parent)
        title = f"Редактирование записи" if record else f"Добавление новой записи"
        self.window.title(title)
        self.window.resizable(False, False)

        self._create_widgets()
        width = EDIT_DIALOG['width']
        height = EDIT_DIALOG['height']
        center_window(self.window, width, height)

    def _setup_placeholder(self, entry, field_name, placeholder_text):
        """Внедряет умный текстовый плейсхолдер в поле Entry."""
        self.placeholders[field_name] = placeholder_text

        # Если это добавление новой записи, сразу пишем подсказку серого цвета
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

        row = 0
        for field in self.meta['fields']:
            field_name = field['name']
            field_label = field['label']
            field_type = field['type']
            editable = field.get('editable', True)
            required = field.get('required', False)
            pk = self.meta.get('pk')

            if not editable and not self.record:
                continue

            label_text = f"{field_label}{'*' if required else ':'}"
            tk.Label(scrollable_frame, text=label_text, anchor='e').grid(
                row=row, column=0, sticky='e', padx=10, pady=5
            )

            current_value = None
            if self.record:
                current_value = self.record.get(field_name)


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
                        if not required: combo.set("[ Не выбрано ]")

                except Exception as e:
                    tk.Label(scrollable_frame, text=f"Ошибка загрузки: {e}").grid(row=row, column=1, padx=10, pady=5)

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
                        clean_eng = ru_label.replace('🟢 ', '').replace('🔴 ', '').replace('🏨 ', '').replace('⚠️ ',
                                                                                                           '').replace(
                            '🧾 ', '').replace('💳 ', '').replace('✅ ', '').replace('❌ ', '').replace('🆕 ', '').replace(
                            '⚙️ ', '').replace('🔒 ', '').replace('💵 ', '').replace('🏦 ', '').replace('📁 ', '')
                        if current_value in ru_label or clean_eng in current_value or (
                                current_value == 'FULFILLED' and 'Заселена' in ru_label):
                            combo.set(ru_label)
                            break
                else:
                    if combo['values']: combo.current(0)

            elif field_type == 'bool':
                combo = ttk.Combobox(scrollable_frame, values=['Да', 'Нет'], state="readonly", width=40)
                combo.grid(row=row, column=1, padx=10, pady=5, sticky='w')
                self.entries[field_name] = combo

                if current_value is not None:
                    combo.set('Да' if current_value else 'Нет')
                else:
                    combo.set('Нет')


            elif field_type == 'text':
                text_widget = tk.Text(scrollable_frame, width=40, height=5)
                text_widget.grid(row=row, column=1, padx=10, pady=5, sticky='w')
                if current_value: text_widget.insert('1.0', current_value)
                self.entries[field_name] = text_widget

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

            if 'maxlen' in field:
                hint = f" (макс. {field['maxlen']} симв.)"
                tk.Label(scrollable_frame, text=hint, font=('Arial', 8)).grid(row=row, column=2, padx=5)

            row += 1

        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=20)

        ttk.Button(btn_frame, text="Сохранить", command=self._save).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self.window.destroy).pack(side=tk.LEFT, padx=10)

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

        if not value: return None

        if field_type in ('int', 'numeric'):
            return int(value) if field_type == 'int' else float(value)

        return value

    def _save(self):
        """Сбор данных и отправка в бэкенд с улучшенной обработкой ошибок БД."""
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

                if not field.get('editable', True):
                    continue

                if field_name == pk_name:
                    continue

                if not editable and self.record:
                    continue

                entry = self.fk_combos.get(field_name) if field_type == 'fk' else self.entries.get(field_name)
                if entry is None:
                    continue

                value = self._get_value(field_name, entry, field_type)

                if required and (value is None or value == ''):
                    raise ValueError(f"Поле '{field['label']}' обязательно для заполнения")

                if value is not None and value != '':
                    if 'min' in field and value < field['min']:
                        raise ValueError(f"Поле '{field['label']}' должно быть не меньше {field['min']}")
                    if 'max' in field and value > field['max']:
                        raise ValueError(f"Поле '{field['label']}' должно быть не больше {field['max']}")
                    if 'maxlen' in field and isinstance(value, str) and len(value) > field['maxlen']:
                        raise ValueError(f"Поле '{field['label']}' не должно превышать {field['maxlen']} символов")

                data[field_name] = value

            if self.record and pk_value is not None:
                self.bl.update(self.table_name, pk_name, pk_value, data)
                messagebox.showinfo("Успех", "Запись успешно обновлена!", parent=self.window)
            else:
                self.bl.insert(self.table_name, data)
                messagebox.showinfo("Успех", "Новая запись успешно добавлена!", parent=self.window)

            self.window.destroy()
            if self.on_save:
                self.on_save()

        except ValueError as e:

            messagebox.showerror(" Ошибка ввода данных", str(e), parent=self.window)

        except Exception as e:

            error_msg = str(e)


            friendly_messages = {
                # Триггерные ошибки
                'Этаж номера превышает количество этажей корпуса':
                    'Номер комнаты не может быть размещен на этаже, которого нет в выбранном корпусе.\n'
                    'Проверьте соответствие этажа и корпуса.',

                'Количество проживающих превышает вместимость номера':
                    'Нельзя заселить больше гостей, чем позволяет вместимость выбранного типа номера.\n'
                    'Выберите номер с большей вместимостью или сократите количество проживающих.',

                'Количество людей в брони не совпадает со списком клиентов':
                    'Количество указанных гостей не соответствует числу людей, добавленных в бронь.\n'
                    'Проверьте, что каждому заявленному месту соответствует реальный клиент в списке.',

                'Количество номеров в брони не совпадает со списком номеров':
                    'Количество заявленных комнат не совпадает с реально привязанными номерами.\n'
                    'Добавьте все необходимые номера в бронь через таблицу "Связь: Бронь - Номера".',

                'Номер уже забронирован на пересекающийся период':
                    'Выбранный номер уже занят другой бронью на эти даты.\n'
                    'Выберите свободный номер или измените даты бронирования.',

                'Проживание можно создать только по активной брони':
                    'Нельзя заселить гостя по отмененной, завершенной или неактивной брони.\n'
                    'Проверьте статус бронирования.',

                'Номер проживания не входит в список номеров данной брони':
                    'Выбранный номер не был зарезервирован в рамках этой брони.\n'
                    'Сначала добавьте этот номер в бронь через таблицу "Связь: Бронь - Номера".',

                'Дата фактического заезда раньше плановой даты брони':
                    'Нельзя заселить гостя раньше даты, указанной в бронировании.\n'
                    'Скорректируйте дату заезда или измените бронь.',

                'Дата фактического выезда позже плановой даты брони':
                    'Нельзя выселить гостя позже даты, указанной в бронировании.\n'
                    'Скорректируйте дату выезда или измените бронь.',

                'Номер не соответствует запрошенной звёздности отеля':
                    'Выбранный номер находится в корпусе, звёздность которого не соответствует брони.\n'
                    'Проверьте запрошенную категорию отеля в параметрах брони.',

                'Номер не соответствует запрошенному этажу':
                    'Выбранный номер находится не на том этаже, который был указан при бронировании.\n'
                    'Выберите номер на нужном этаже или измените пожелания в брони.',

                'Услуга.*недоступна в корпусе':
                    'Данная услуга не предоставляется в выбранном корпусе.\n'
                    'Проверьте список доступных услуг для этого корпуса.',

                'Дата использования услуги не входит в период проживания':
                    'Услуга не может быть оказана вне периода проживания гостя.\n'
                    'Проверьте дату использования — она должна быть между датами заезда и выезда.',

                'Все номера данной брони должны находиться на одном этаже':
                    'В брони установлен флаг "Селять на одном этаже", но номера находятся на разных этажах.\n'
                    'Выберите номера, расположенные на одном этаже, или отключите это ограничение.',

                'Сумма оплат превышает сумму счёта':
                    'Нельзя внести оплату, превышающую общую сумму счета.\n'
                    'Проверьте корректность вводимой суммы.',

                'Назначенные номера не соответствуют новой запрошенной звёздности':
                    'Нельзя изменить требуемую звёздность брони, так как уже назначенные номера ей не соответствуют.\n'
                    'Сначала измените список номеров в брони.',

                'Назначенные номера не соответствуют новому запрошенному этажу':
                    'Нельзя изменить желаемый этаж, так как уже назначенные номера находятся на других этажах.\n'
                    'Сначала измените список номеров в брони.',

                'Нельзя включить keep_on_same_floor':
                    'Нельзя установить флаг "Селять на одном этаже", так как номера брони уже находятся на разных этажах.\n'
                    'Сначала переместите все номера на один этаж.',

                'Невозможно рассчитать штраф':
                    'Система не может рассчитать штраф за отмену брони, так как не все номера были назначены.\n'
                    'Обратитесь к администратору для ручного расчета.',

                # Ошибки целостности PostgreSQL
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

                full_message = (
                    f"{friendly_message}\n\n"

                    # f"Техническая информация:\n"
                    #f"{error_msg.split('CONTEXT:')[0].strip()}"
                )
                messagebox.showerror(" Ошибка сохранения", full_message, parent=self.window)
            else:

                messagebox.showerror(
                    " Ошибка базы данных",
                    f"Произошла ошибка при сохранении данных.\n\n"
                    f"Техническая информация:\n{error_msg.split('CONTEXT:')[0].strip()}\n\n",
                    parent=self.window
                )