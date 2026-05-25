"""Форматирование данных из БД в человекочитаемый вид."""

import datetime
from gui.constants import STATUS_LABELS, FIELD_PLACEHOLDERS, REPORT_COLUMNS


class DataFormatter:
    """Класс-декоратор для преобразования сырых данных из БД."""


    STATUS_LABELS = STATUS_LABELS
    FIELD_PLACEHOLDERS = FIELD_PLACEHOLDERS
    REPORT_COLUMNS = REPORT_COLUMNS

    @classmethod
    def decorate_main_row(cls, bl, row):
        """Очеловечивает одну строку для отображения в Treeview."""
        new_row = row.copy()


        for field in ['status', 'method']:
            if field in new_row and new_row[field] in STATUS_LABELS:
                new_row[field] = STATUS_LABELS[new_row[field]]


        if new_row.get('client_id') is not None:
            client = bl.get_by_id('client', 'client_id', row['client_id'])
            if client:
                last = client.get('last_name', '')
                first = client.get('first_name', '')
                new_row['client_id'] = f"{last} {first[:1]}." if first else last


        if new_row.get('room_id') is not None:
            room = bl.get_by_id('room', 'room_id', row['room_id'])
            if room:
                new_row['room_id'] = f"Комната № {room.get('room_number')}"

        if 'contract_id' in new_row:
            if row['contract_id']:
                contract = bl.get_by_id('contract', 'contract_id', row['contract_id'])
                new_row['contract_id'] = f"Договор № {contract.get('contract_number')}" if contract else f"#{row['contract_id']}"
            else:
                new_row['contract_id'] = "—"

        if new_row.get('building_id') is not None:
            bld = bl.get_by_id('building', 'building_id', row['building_id'])
            if bld:
                new_row['building_id'] = bld.get('name')

        if new_row.get('invoice_id') is not None:
            new_row['invoice_id'] = f"Счёт № {row['invoice_id']}"

        if new_row.get('stay_id') is not None:
            new_row['stay_id'] = f"Проживание № {row['stay_id']}"

        if 'booking_id' in new_row:
            new_row['booking_id'] = f"Бронь № {row['booking_id']}" if row['booking_id'] else "Без брони"


        if new_row.get('service_type_id') is not None:
            st = bl.get_by_id('service_type', 'service_type_id', row['service_type_id'])
            if st:
                new_row['service_type_id'] = st.get('name')

        if new_row.get('building_type_id') is not None:
            bt = bl.get_by_id('building_type', 'building_type_id', row['building_type_id'])
            if bt:
                new_row['building_type_id'] = bt.get('name')

        if new_row.get('room_type_id') is not None:
            rt = bl.get_by_id('room_type', 'room_type_id', row['room_type_id'])
            if rt:
                new_row['room_type_id'] = rt.get('name')

        for key, value in new_row.items():
            if isinstance(value, datetime.datetime):
                new_row[key] = value.strftime('%Y-%m-%d %H:%M')

        return new_row

    @classmethod
    def get_report_label(cls, col_name):
        """Получить читаемое название колонки для отчёта."""
        return REPORT_COLUMNS.get(col_name, col_name.replace('_', ' ').title())