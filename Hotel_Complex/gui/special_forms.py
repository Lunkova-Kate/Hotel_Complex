import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from gui.sizes import CHECKIN_FORM, CHECKOUT_FORM, CANCEL_BOOKING_FORM, ADD_PAYMENT_FORM
from gui.utils import center_window


class CheckinForm:
    """Модернизированная человекочитаемая форма заселения гостей."""

    def __init__(self, parent, business_logic, on_success=None):
        self.parent = parent
        self.bl = business_logic
        self.on_success = on_success

        self.window = tk.Toplevel(parent)
        self.window.title("Регистрация заселения (Фронт-офис)")

        width = CHECKIN_FORM['width']
        height = CHECKIN_FORM['height']
        self.window.geometry(f"{width}x{height}")
        self.window.resizable(False, False)
        center_window(self.window, width, height)

        self.window.transient(parent)
        self.window.grab_set()

        self._create_widgets()

    def _create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text="Регистрация нового проживания", font=('Arial', 14, 'bold')).pack(pady=(0, 15))

        room_frame = ttk.LabelFrame(main_frame, text=" Выбор номера и времени ", padding="10")
        room_frame.pack(fill=tk.X, pady=5)

        tk.Label(room_frame, text="Свободный номер:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.room_combo = ttk.Combobox(room_frame, width=40, state="readonly")
        self.room_combo.grid(row=0, column=1, padx=5, pady=5)

        try:
            rooms = self.bl.get_fk_options('room', 'room_number')
            self.room_mapping = {f"Комната № {num}": r_id for r_id, num in rooms}
            self.room_combo['values'] = list(self.room_mapping.keys())
        except Exception:
            self.room_combo['values'] = ["Ошибка загрузки списка номеров"]

        tk.Label(room_frame, text="Дата заезда:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.checkin_entry = ttk.Entry(room_frame, width=25)
        self.checkin_entry.insert(0, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.checkin_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)

        guests_frame = ttk.LabelFrame(main_frame, text=" Выберите проживающих гостей из списка ", padding="10")
        guests_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.client_tree = ttk.Treeview(guests_frame, columns=('fio', 'passport'), show='headings', height=8)
        self.client_tree.heading('fio', text='ФИО Клиента')
        self.client_tree.heading('passport', text='Паспортные данные')
        self.client_tree.column('fio', width=300)
        self.client_tree.column('passport', width=150)

        scroll = ttk.Scrollbar(guests_frame, orient="vertical", command=self.client_tree.yview)
        self.client_tree.configure(yscrollcommand=scroll.set)
        self.client_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.client_id_map = {}
        try:
            clients = self.bl.get_all('client', limit=300)
            for c in clients:
                fio = f"{c['last_name']} {c['first_name']}".strip()
                row_id = self.client_tree.insert('', tk.END, values=(fio, c['passport_number']))
                self.client_id_map[row_id] = c['client_id']
        except Exception as e:
            print(f"Ошибка заполнения списка гостей: {e}")

        self.client_tree.configure(selectmode='extended')
        tk.Label(main_frame, text="* Зажмите Ctrl или Shift, чтобы выбрать несколько человек в один номер",
                 font=('Arial', 8, 'italic'), fg='gray').pack(anchor='w')


        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Заселить", command=self._checkin, width=15).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self.window.destroy, width=15).pack(side='left', padx=10)

    def _checkin(self):
        try:
            selected_room = self.room_combo.get()
            if not selected_room:
                raise ValueError("Пожалуйста, выберите номер комнаты!")
            room_id = self.room_mapping[selected_room]

            checkin_time = self.checkin_entry.get().strip()
            datetime.strptime(checkin_time, '%Y-%m-%d %H:%M:%S')

            selected_rows = self.client_tree.selection()
            if not selected_rows:
                raise ValueError("Не выбран ни один гость для заселения!")

            client_ids = [self.client_id_map[row] for row in selected_rows]

            self.bl.checkin(room_id, client_ids, checkin_time, booking_id=None)

            messagebox.showinfo("Успех", "Заселение успешно оформлено!", parent=self.window)
            self.window.destroy()
            if self.on_success:
                self.on_success()

        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e), parent=self.window)
        except Exception as e:
            messagebox.showerror("Ошибка СУБД", f"Операция отклонена базой данных:\n{str(e)}", parent=self.window)


class CheckoutForm:
    """Модернизированная форма выселения гостей (регистрация выезда)."""

    def __init__(self, parent, business_logic, on_success=None):
        self.parent = parent
        self.bl = business_logic
        self.on_success = on_success

        self.window = tk.Toplevel(parent)
        self.window.title("Регистрация выезда (Выселение)")

        width = CHECKOUT_FORM['width']
        height = CHECKOUT_FORM['height']
        self.window.geometry(f"{width}x{height}")
        self.window.resizable(False, False)
        center_window(self.window, width, height)

        self.window.transient(parent)
        self.window.grab_set()

        self._create_widgets()

    def _create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text="Оформление выезда гостя", font=('Arial', 14, 'bold')).pack(pady=(0, 15))

        stay_frame = ttk.LabelFrame(main_frame, text=" Активные проживания в отеле ", padding="10")
        stay_frame.pack(fill=tk.X, pady=5)

        tk.Label(stay_frame, text="Выберите проживание:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.stay_combo = ttk.Combobox(stay_frame, width=55, state="readonly")
        self.stay_combo.grid(row=0, column=1, padx=5, pady=5)

        self.stay_mapping = {}
        try:
            stays = self.bl.get_all('stay', limit=200)
            rooms = {r['room_id']: r['room_number'] for r in self.bl.get_all('room', limit=200)}

            combo_values = []
            for s in stays:
                if s.get('checkout_at') is None:
                    r_num = rooms.get(s['room_id'], s['room_id'])
                    label = f"Комната №{r_num} (Заезд: {s['checkin_at']}) [ID: {s['stay_id']}]"
                    self.stay_mapping[label] = s['stay_id']
                    combo_values.append(label)

            self.stay_combo['values'] = combo_values
        except Exception as e:
            self.stay_combo['values'] = ["Ошибка загрузки списка проживаний"]

        tk.Label(stay_frame, text="Дата/время выезда:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.checkout_entry = ttk.Entry(stay_frame, width=25)
        self.checkout_entry.insert(0, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.checkout_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Оформить выезд", command=self._checkout, width=18).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self.window.destroy, width=15).pack(side='left', padx=10)

    def _checkout(self):
        try:
            selected_stay = self.stay_combo.get()
            if not selected_stay:
                raise ValueError("Пожалуйста, выберите активное проживание!")
            stay_id = self.stay_mapping[selected_stay]

            checkout_time = self.checkout_entry.get().strip()
            datetime.strptime(checkout_time, '%Y-%m-%d %H:%M:%S')

            self.bl.checkout(stay_id, checkout_time)

            messagebox.showinfo("Успех", "Выезд гостя успешно оформлен!", parent=self.window)
            self.window.destroy()
            if self.on_success:
                self.on_success()

        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e), parent=self.window)
        except Exception as e:
            messagebox.showerror("Ошибка СУБД", f"Не удалось оформить выезд:\n{str(e)}", parent=self.window)


class CancelBookingForm:
    """Форма отмены бронирования."""

    def __init__(self, parent, business_logic, on_success=None):
        self.parent = parent
        self.bl = business_logic
        self.on_success = on_success

        self.window = tk.Toplevel(parent)
        self.window.title("Отмена бронирования")

        from gui.sizes import CANCEL_BOOKING_FORM
        width = CANCEL_BOOKING_FORM['width']
        height = CANCEL_BOOKING_FORM['height']
        self.window.geometry(f"{width}x{height}")
        self.window.resizable(False, False)

        from gui.utils import center_window
        center_window(self.window, width, height)

        self.window.transient(parent)
        self.window.grab_set()

        self._create_widgets()

    def _create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text="Отмена существующей брони", font=('Arial', 14, 'bold')).pack(pady=(0, 15))

        booking_frame = ttk.LabelFrame(main_frame, text=" Выберите активную бронь ", padding="10")
        booking_frame.pack(fill=tk.X, pady=5)

        tk.Label(booking_frame, text="Бронирование:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.booking_combo = ttk.Combobox(booking_frame, width=55, state="readonly")
        self.booking_combo.grid(row=0, column=1, padx=5, pady=5)

        self.booking_mapping = {}
        try:
            bookings = self.bl.get_all('booking', limit=200)
            combo_values = []
            for b in bookings:
                if b['status'] == 'ACTIVE':
                    label = f"Бронь №{b['booking_id']} (План заезда: {b['planned_checkin']}) [Мест: {b['people_count']}]"
                    self.booking_mapping[label] = b['booking_id']
                    combo_values.append(label)
            self.booking_combo['values'] = combo_values
        except Exception:
            self.booking_combo['values'] = ["Ошибка загрузки списка броней"]

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Аннулировать бронь", command=self._cancel, width=20).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self.window.destroy, width=15).pack(side='left', padx=10)

    def _cancel(self):
        try:
            selected = self.booking_combo.get()
            if not selected or "Ошибка" in selected:
                raise ValueError("Пожалуйста, выберите корректную бронь из списка!")

            booking_id = self.booking_mapping[selected]


            self.bl.cancel_booking(booking_id)

            from tkinter import messagebox
            messagebox.showinfo("Успех", f"Бронь №{booking_id} успешно аннулирована!", parent=self.window)

            self.window.destroy()
            if self.on_success:
                self.on_success()

        except PermissionError as e:
            from tkinter import messagebox
            messagebox.showerror("Ошибка доступа", str(e), parent=self.window)
        except ValueError as e:
            from tkinter import messagebox
            messagebox.showerror("Ошибка", str(e), parent=self.window)
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Ошибка", f"Не удалось отменить бронь:\n{e}", parent=self.window)


class AddPaymentForm:

    def __init__(self, parent, business_logic, on_success=None):
        self.parent = parent
        self.bl = business_logic
        self.on_success = on_success

        self.window = tk.Toplevel(parent)
        self.window.title("Регистрация оплаты")

        width = ADD_PAYMENT_FORM['width']
        height = ADD_PAYMENT_FORM['height']
        self.window.geometry(f"{width}x{height}")
        self.window.resizable(False, False)
        center_window(self.window, width, height)

        self.window.transient(parent)
        self.window.grab_set()

        self._create_widgets()

    def _create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text="Проведение оплаты по счёту", font=('Arial', 14, 'bold')).pack(pady=(0, 15))

        pay_frame = ttk.LabelFrame(main_frame, text=" Параметры платежа ", padding="10")
        pay_frame.pack(fill=tk.X, pady=5)

        tk.Label(pay_frame, text="Выберите счёт для оплаты:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.invoice_combo = ttk.Combobox(pay_frame, width=55, state="readonly")
        self.invoice_combo.grid(row=0, column=1, padx=5, pady=5)

        self.invoice_mapping = {}
        try:
            invoices = self.bl.get_all('invoice', limit=500)
            combo_values = []
            for inv in invoices:
                status = inv.get('status', '')

                if status.upper() in ('OPEN', 'PARTIALLY_PAID'):
                    room = float(inv.get('room_amount', 0) or 0)
                    service = float(inv.get('service_amount', 0) or 0)
                    penalty = float(inv.get('penalty_amount', 0) or 0)
                    total = room + service + penalty

                    paid = 0.0
                    try:
                        payments = self.bl.get_all('payment', limit=500)
                        for p in payments:
                            if p.get('invoice_id') == inv['invoice_id']:
                                paid += float(p.get('amount', 0) or 0)
                    except Exception:
                        pass

                    debt = total - paid

                    if debt > 0:
                        status_label = 'Открыт' if status.upper() == 'OPEN' else 'Частично оплачен'
                        label = (f"Счёт №{inv['invoice_id']} "
                                 f"[{status_label}] "
                                 f"— Долг: {debt:,.2f} руб.")
                        self.invoice_mapping[label] = inv['invoice_id']
                        combo_values.append(label)

            if combo_values:
                self.invoice_combo['values'] = combo_values
                self.invoice_combo.current(0)
            else:
                self.invoice_combo['values'] = ["Нет счетов к оплате"]

        except Exception:
            self.invoice_combo['values'] = ["Ошибка загрузки неоплаченных счетов"]


        tk.Label(pay_frame, text="Сумма платежа (руб.):").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.amount_entry = ttk.Entry(pay_frame, width=25)
        self.amount_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)


        tk.Label(pay_frame, text="Способ оплаты:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.method_combo = ttk.Combobox(pay_frame, values=['💵 Наличные', '💳 Банковская карта', '🏦 Банковский перевод', '📁 Другое'], state="readonly", width=22)
        self.method_combo.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        self.method_combo.current(0)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Провести платёж", command=self._add_payment, width=18).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self.window.destroy, width=15).pack(side='left', padx=10)

    def _add_payment(self):
        try:
            selected_invoice = self.invoice_combo.get()
            if not selected_invoice:
                raise ValueError("Пожалуйста, выберите счёт для оплаты!")
            invoice_id = self.invoice_mapping[selected_invoice]

            amount_str = self.amount_entry.get().strip()
            if not amount_str:
                raise ValueError("Введите сумму платежа!")
            amount = float(amount_str)


            raw_method = self.method_combo.get()
            if 'Наличные' in raw_method: method = 'CASH'
            elif 'карта' in raw_method: method = 'CARD'
            elif 'перевод' in raw_method: method = 'TRANSFER'
            else: method = 'OTHER'

            self.bl.add_payment(invoice_id, amount, method)

            messagebox.showinfo("Успех", "Оплата успешно принята и проведена!", parent=self.window)
            self.window.destroy()
            if self.on_success:
                self.on_success()

        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e), parent=self.window)
        except Exception as e:
            messagebox.showerror("Ошибка СУБД", f"Платёж отклонён базой данных:\n{str(e)}", parent=self.window)