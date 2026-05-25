import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Data_Acces.db_connection import DatabaseConnection
from Data_Acces.universal_dao import UniversalDAO
from Data_Acces import query_handlers as qh
from Core.role_permissions import can


class BusinessLogic:
    def __init__(self, role):
        self.role = role

    def can_read(self, table_name):
        if self.role == 'admin':
            return True
        return can(self.role, 'read', table_name)

    def can_write(self, table_name):
        if self.role == 'admin':
            return True
        return can(self.role, 'write', table_name)

    def can_delete(self, table_name):
        if self.role == 'admin':
            return True
        return can(self.role, 'delete', table_name)

    def get_all(self, table_name, limit=100, offset=0, order_by=None):
        if not self.can_read(table_name):
            raise PermissionError(f"Нет прав на чтение {table_name}")
        return UniversalDAO.get_all(table_name, limit, offset, order_by)

    def get_by_id(self, table_name, pk_name, pk_value):
        if not self.can_read(table_name):
            raise PermissionError(f"Нет прав на чтение {table_name}")
        return UniversalDAO.get_by_id(table_name, pk_name, pk_value)

    def insert(self, table_name, data):
        if not self.can_write(table_name):
            raise PermissionError(f"Нет прав на вставку в {table_name}")
        return UniversalDAO.insert(table_name, data)

    def update(self, table_name, pk_name, pk_value, data):
        if not self.can_write(table_name):
            raise PermissionError(f"Нет прав на обновление {table_name}")
        return UniversalDAO.update(table_name, pk_name, pk_value, data)

    def delete(self, table_name, pk_name, pk_value):
        if not self.can_delete(table_name):
            raise PermissionError(f"Нет прав на удаление из {table_name}")
        return UniversalDAO.delete(table_name, pk_name, pk_value)

    def get_fk_options(self, ref_table, display_col, id_col=None):
        if not self.can_read(ref_table):
            raise PermissionError(f"Нет прав на чтение {ref_table}")
        return UniversalDAO.get_fk_options(ref_table, display_col, id_col)

    # Сложные операции
    def checkin(self, room_id, client_ids, checkin_time, booking_id=None):
        if self.role not in ['admin', 'manager']:
            raise PermissionError("Недостаточно прав")
        if not client_ids:
            raise ValueError("Список клиентов не может быть пустым")

        with DatabaseConnection() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO stay (room_id, booking_id, checkin_at, checkout_at)
                        VALUES (%s, %s, %s, NULL) RETURNING stay_id
                    """, (room_id, booking_id, checkin_time))
                    stay_id = cur.fetchone()[0]

                    for client_id in client_ids:
                        cur.execute("""
                            INSERT INTO stay_client (stay_id, client_id) VALUES (%s, %s)
                        """, (stay_id, client_id))

                    return stay_id

    def checkout(self, stay_id, checkout_time):
        if self.role not in ['admin', 'manager']:
            raise PermissionError("Недостаточно прав")
        with DatabaseConnection() as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE stay SET checkout_at = %s
                        WHERE stay_id = %s AND checkout_at IS NULL
                    """, (checkout_time, stay_id))
                    if cur.rowcount == 0:
                        raise ValueError("Проживание не найдено или уже завершено")

    def add_payment(self, invoice_id, amount, method, paid_at=None):
        if self.role not in ['admin', 'manager']:
            raise PermissionError("Недостаточно прав")
        with DatabaseConnection() as conn:
            with conn:
                with conn.cursor() as cur:
                    if paid_at:
                        cur.execute("""
                            INSERT INTO payment (invoice_id, paid_at, amount, method)
                            VALUES (%s, %s, %s, %s) RETURNING payment_id
                        """, (invoice_id, paid_at, amount, method))
                    else:
                        cur.execute("""
                            INSERT INTO payment (invoice_id, paid_at, amount, method)
                            VALUES (%s, now(), %s, %s) RETURNING payment_id
                        """, (invoice_id, amount, method))
                    return cur.fetchone()[0]

    def cancel_booking(self, booking_id):
        if not self.can_write('booking'):
            raise PermissionError("Нет прав на отмену брони")
        booking = UniversalDAO.get_by_id('booking', 'booking_id', booking_id)
        if not booking:
            raise ValueError("Бронь не найдена")
        if booking['status'] != 'ACTIVE':
            raise ValueError("Можно отменить только активную бронь")
        return UniversalDAO.update('booking', 'booking_id', booking_id, {'status': 'CANCELLED'})



    def get_all_paginated(self, table_name, page=1, per_page=50, order_by=None):
        """Получить записи с пагинацией (с проверкой прав)."""
        if not self.can_read(table_name):
            raise PermissionError(f"Нет прав на чтение {table_name}")
        return UniversalDAO.get_all_paginated(table_name, page, per_page, order_by)

    # Отчёты (все 16)
    def report_free_rooms_count(self):
        return qh.get_free_rooms_count()

    def report_room_free_info(self, room_id):
        return qh.get_room_free_info(room_id)

    def report_guests_by_room_features(self, stars, min_capacity, start_date, end_date):
        return qh.get_guests_by_room_features(stars, min_capacity, start_date, end_date)

    def report_firms_by_volume(self, min_people, start_date=None, end_date=None):
        return qh.get_firms_by_volume(min_people, start_date, end_date)

    def report_unhappy_clients(self):
        return qh.get_unhappy_clients_with_complaints()

    def report_new_clients(self, start_date, end_date):
        return qh.get_new_clients(start_date, end_date)

    def report_client_full_history(self, client_id):
        return qh.get_client_full_history(client_id)

    def report_room_occupants(self, room_id, start_ts, end_ts):
        return qh.get_room_occupants(room_id, start_ts, end_ts)

    def report_partner_percentage(self):
        return qh.get_partner_booking_percentage()

    # Дополнительные отчёты для GUI
    def report_free_rooms_by_features(self, stars, min_capacity, moment):
        return qh.get_free_rooms_by_features(stars, min_capacity, moment)

    def report_occupied_rooms_free_by_deadline(self, reference_ts, deadline_ts):
        return qh.get_occupied_rooms_free_by_deadline(reference_ts, deadline_ts)

    def report_booking_volume_and_preferences(self, org_name, start_date, end_date):
        return qh.get_booking_volume_and_preferences(org_name, start_date, end_date)

    def report_profitability(self, start_date, end_date):
        return qh.get_profitability(start_date, end_date)

    def report_guest_info_by_room(self, room_id):
        return qh.get_guest_info_by_room(room_id)

    def report_firms_with_contracts_period(self, start_date, end_date):
        return qh.get_firms_with_contracts_period(start_date, end_date)

    def report_frequent_guests_all(self):
        return qh.get_frequent_guests_all()