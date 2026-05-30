"""
Централизованные константы приложения.
Все текстовые маппинги, лейблы, названия таблиц и статусов.
"""

#  НАЗВАНИЯ ТАБЛИЦ ДЛЯ БОКОВОГО МЕНЮ

TABLE_DISPLAY_NAMES = {
    # Основные таблицы
    'client': '👥 Клиенты',
    'booking': '📅 Бронирования',
    'stay': '🏨 Проживания (Заселения)',
    'room': '🛏 Номерной фонд',
    'room_tariff': '💵 Тарифы на номера',
    'building': '🏢 Корпуса',
    'service_type': '🛠 Дополнительные услуги',
    'service_usage': '📊 Использование услуг',
    'invoice': '🧾 Счета на оплату',
    'payment': '💳 Платежи',
    'complaint': '⚠️ Жалобы клиентов',
    'review': '⭐ Отзывы',
    'organization': '🏢 Организации-партнёры',
    'contract': '📜 Договоры',

    'booking_room': '🔗 Связь: Бронь - Номера',
    'booking_client': '🔗 Связь: Бронь - Клиенты',
    'stay_client': '🔗 Связь: Проживание - Клиенты',
    'building_service': '🔗 Связь: Корпус - Услуги',

    'building_type': '⚙️ Справочник: Типы корпусов',
    'organization_type': '⚙️ Справочник: Типы организаций',
    'room_type': '⚙️ Справочник: Категории комнат',


    'organization_tour_agency': '🏢 Турфирмы (лицензии)',
    'organization_event_organizer': '🎤 Организаторы мероприятий',


    'penalty': '⚠️ Штрафы за нарушения',
    'financial_penalty': '💰 Финансовые штрафы (отмены)',


    'expense': '📉 Расходы гостиницы',
}


#  НАЗВАНИЯ ТАБЛИЦ ДЛЯ ОКНА ДЕТАЛЬНОГО ПРОСМОТРА

DETAIL_VIEW_TABLE_NAMES = {
    'client': 'Клиент',
    'booking': 'Бронирование',
    'stay': 'Проживание',
    'room': 'Номер',
    'room_tariff': 'Тариф',
    'building': 'Корпус',
    'service_type': 'Услуга',
    'service_usage': 'Использование услуги',
    'invoice': 'Счёт',
    'payment': 'Платёж',
    'complaint': 'Жалоба',
    'review': 'Отзыв',
    'organization': 'Организация',
    'contract': 'Договор',
    'penalty': 'Штраф',
    'financial_penalty': 'Финансовый штраф',
    'expense': 'Расход',
    'building_type': 'Тип корпуса',
    'room_type': 'Тип номера',
    'organization_type': 'Тип организации',
    'organization_tour_agency': 'Турфирма',
    'organization_event_organizer': 'Организатор мероприятий',
    'booking_room': 'Связь: Бронь — Номер',
    'booking_client': 'Связь: Бронь — Клиент',
    'stay_client': 'Связь: Проживание — Клиент',
    'building_service': 'Связь: Корпус — Услуга',
}


#  СТАТУСЫ (БД в Человекочитаемый вид)

STATUS_LABELS = {
    # Статусы бронирования
    'ACTIVE': '🟢 Активна',
    'CANCELLED': '🔴 Отменена',
    'FULFILLED': '🏨 Заселена',
    'NO_SHOW': '⚠️ Неявка',


    'OPEN': '🧾 Открыт',
    'PARTIALLY_PAID': '💳 Частично оплачен',
    'PAID': '✅ Оплачен',

    'NEW': '🆕 Новая',
    'IN_PROGRESS': '⚙️ В работе',
    'CLOSED': '🔒 Закрыта',


    'CASH': '💵 Наличные',
    'CARD': '💳 Карта',
    'TRANSFER': '🏦 Перевод',
    'OTHER': '📁 Другое',
}




STATUS_CHOICES = {
    'booking': ['🟢 Активна', '🔴 Отменена', '🏨 Заселена (Выполнена)', '⚠️ Гость не явился'],
    'invoice': ['🧾 Открыт (Не оплачен)', '💳 Оплачен частично', '✅ Оплачен полностью', '❌ Аннулирован'],
    'complaint': ['🆕 Новая', '⚙️ В работе', '🔒 Закрыта'],
}

METHOD_CHOICES = ['💵 Наличные', '💳 Банковская карта', '🏦 Банковский перевод', '📁 Другое']


#  ОБРАТНЫЙ ПЕРЕВОД

REVERSE_STATUS_MAP = {
    'Активна': 'ACTIVE',
    'Отменена': 'CANCELLED',
    'Заселена': 'FULFILLED',
    'Неявка': 'NO_SHOW',
    'Открыт': 'OPEN',
    'Частично': 'PARTIALLY_PAID',
    'Полностью': 'PAID',
    'Аннулирован': 'CANCELLED',
    'Новая': 'NEW',
    'В работе': 'IN_PROGRESS',
    'Закрыта': 'CLOSED',
    'Наличные': 'CASH',
    'Карта': 'CARD',
    'Перевод': 'TRANSFER',
    'Другое': 'OTHER',
}


#  ФОРМАТЫ ДАТ

DATE_FORMAT = '%Y-%m-%d'
TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M'
TIMESTAMP_FORMAT_FULL = '%Y-%m-%d %H:%M:%S'
DATE_DISPLAY_FORMAT = '%d.%m.%Y'
TIMESTAMP_DISPLAY_FORMAT = '%d.%m.%Y %H:%M'


#  ПОДСКАЗКТ ДЛЯ ПОЛЕЙ ВВОДА

FIELD_PLACEHOLDERS = {
    'date': 'ГГГГ-ММ-ДД',
    'timestamp': 'ГГГГ-ММ-ДД ЧЧ:ММ',
    'phone': '+7 (999) 111-22-33',
    'email': 'example@hotel.ru',
}

#  НАЗВАНИЯ КОЛОНОК ДЛЯ ОТЧЁТОВ

REPORT_COLUMNS = {
    'organization_id': 'ID Организации',
    'name': 'Название / Имя',
    'total_people': 'Всего человек (мест)',
    'client_id': 'ID Клиента',
    'first_name': 'Имя',
    'last_name': 'Фамилия',
    'total_clients': 'Всего постояльцев',
    'free_rooms_count': 'Свободных номеров',
    'room_id': 'ID Номера',
    'room_number': 'Номер комнаты',
    'floor_no': 'Этаж',
    'floor': 'Этаж',
    'building': 'Корпус',
    'building_name': 'Название корпуса',
    'hotel_stars': 'Звёздность',
    'room_type': 'Тип номера',
    'capacity': 'Вместимость',
    'price_per_night': 'Цена за ночь',
    'is_free_now': 'Свободен сейчас',
    'next_occupancy_start': 'Ближайшее заселение',
    'checkin_at': 'Дата заезда',
    'checkout_time': 'Дата выезда',
    'hours_until_free': 'Часов до освобождения',
    'bookings_count': 'Кол-во бронирований',
    'total_rooms_booked': 'Забронировано номеров',
    'total_people_booked': 'Забронировано мест',
    'times_selected': 'Кол-во выборов',
    'percentage': 'Доля (%)',
    'complaint_id': 'ID Жалобы',
    'text': 'Текст',
    'complaint_text': 'Текст жалобы',
    'status': 'Статус',
    'complaint_status': 'Статус жалобы',
    'room_sales': 'Выручка с номеров (руб.)',
    'overhead_costs': 'Расходы корпуса (руб.)',
    'profitability_ratio': 'Коэффициент рентабельности',
    'service_invoice_amount': 'Счёт за услуги (руб.)',
    'complaint_date': 'Дата подачи жалобы',
    'service_type_id': 'ID Услуги',
    'service_name': 'Название услуги',
    'used_at': 'Дата использования',
    'quantity': 'Количество',
    'phone': 'Телефон',
    'email': 'Email',
    'contract_number': 'Номер договора',
    'valid_from': 'Действует с',
    'valid_to': 'Действует по',
    'visits_count': 'Кол-во визитов',
    'buildings_visited': 'Посещено корпусов',
    'first_visit': 'Первый визит',
    'last_visit': 'Последний визит',
    'created_at': 'Дата регистрации',
    'invoice_id': '№ Счёта',
    'invoice_created_at': 'Дата выставления счёта',
    'invoice_status': 'Статус счёта',
    'room_amount': 'Сумма за проживание',
    'service_amount': 'Сумма за услуги',
    'penalty_amount': 'Сумма штрафов',
    'total_invoice_amount': 'Итого по счёту',
    'payment_id': '№ Платёж',
    'paid_at': 'Дата оплаты',
    'paid_amount': 'Оплачено',
    'method': 'Способ оплаты',
    'partner_bookings': 'Брони партнеров',
    'total_bookings': 'Всего бронирований',
    'partner_percentage': 'Доля партнерских броней (%)',
}


#  РОЛИ ПОЛЬЗОВАТЕЛЕЙ

ROLE_NAMES = {
    'admin': 'Администратор',
    'manager': 'Менеджер',
}


#  НАСТРОЙКИ ТАБЛИЦ (шрифты)

TREEVIEW_CONFIG = {
    'heading_font': ('Arial', 11, 'bold'),
    'row_font': ('Arial', 11),
    'row_height': 32,
}