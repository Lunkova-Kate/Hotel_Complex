TABLES_META = {
    'building_type': {
        'pk': 'building_type_id',
        'fields': [
            {'name': 'building_type_id', 'label': 'ID', 'type': 'int', 'editable': False},
            {'name': 'name', 'label': 'Название', 'type': 'str', 'required': True, 'maxlen': 100},
            {'name': 'hotel_stars', 'label': 'Звёздность (2-5)', 'type': 'int', 'required': True, 'min': 2, 'max': 5},
        ]
    },
    'building': {
        'pk': 'building_id',
        'fields': [
            {'name': 'building_id', 'label': 'ID', 'type': 'int', 'editable': False},
            {'name': 'building_type_id', 'label': 'Тип корпуса', 'type': 'fk', 'ref_table': 'building_type', 'display_col': 'name', 'required': True},
            {'name': 'name', 'label': 'Название', 'type': 'str', 'required': True, 'maxlen': 120},
            {'name': 'floors_count', 'label': 'Кол-во этажей', 'type': 'int', 'required': True, 'min': 1},
        ]
    },
    'room_type': {
        'pk': 'room_type_id',
        'fields': [
            {'name': 'room_type_id', 'label': 'ID', 'type': 'int', 'editable': False},
            {'name': 'name', 'label': 'Название', 'type': 'str', 'required': True, 'maxlen': 100},
            {'name': 'capacity', 'label': 'Вместимость (чел.)', 'type': 'int', 'required': True, 'min': 1},
        ]
    },
    'room': {
        'pk': 'room_id',
        'fields': [
            {'name': 'room_id', 'label': 'ID', 'type': 'int', 'editable': False},
            {'name': 'building_id', 'label': 'Корпус', 'type': 'fk', 'ref_table': 'building', 'display_col': 'name', 'required': True},
            {'name': 'room_type_id', 'label': 'Тип номера', 'type': 'fk', 'ref_table': 'room_type', 'display_col': 'name', 'required': True},
            {'name': 'floor_no', 'label': 'Этаж', 'type': 'int', 'required': True, 'min': 1},
            {'name': 'room_number', 'label': 'Номер комнаты', 'type': 'str', 'required': True, 'maxlen': 20},
        ]
    },
    'service_type': {
        'pk': 'service_type_id',
        'fields': [
            {'name': 'service_type_id', 'label': 'ID', 'type': 'int', 'editable': False},
            {'name': 'name', 'label': 'Название услуги', 'type': 'str', 'required': True, 'maxlen': 120},
            {'name': 'category', 'label': 'Категория', 'type': 'str', 'required': True, 'maxlen': 50},
            {'name': 'unit', 'label': 'Единица измерения', 'type': 'str', 'required': True, 'maxlen': 30},
            {'name': 'base_price', 'label': 'Базовая цена', 'type': 'numeric', 'required': True, 'min': 0},
        ]
    },
    'building_service': {
        'pk': None,
        'fields': [
            {'name': 'building_id', 'label': 'Корпус', 'type': 'fk', 'ref_table': 'building', 'display_col': 'name', 'required': True},
            {'name': 'service_type_id', 'label': 'Услуга', 'type': 'fk', 'ref_table': 'service_type', 'display_col': 'name', 'required': True},
            {'name': 'pay_per_use', 'label': 'Платно при использовании', 'type': 'bool', 'required': True},
        ]
    },
    'organization_type': {
        'pk': 'organization_type_id',
        'fields': [
            {'name': 'organization_type_id', 'label': 'ID', 'type': 'int', 'editable': False},
            {'name': 'name', 'label': 'Название типа', 'type': 'str', 'required': True, 'maxlen': 120},
        ]
    },
    'organization': {
        'pk': 'organization_id',
        'fields': [
            {'name': 'organization_id', 'label': 'ID', 'type': 'int', 'editable': False},
            {'name': 'organization_type_id', 'label': 'Тип организации', 'type': 'fk', 'ref_table': 'organization_type', 'display_col': 'name', 'required': True},
            {'name': 'name', 'label': 'Название', 'type': 'str', 'required': True, 'maxlen': 200},
            {'name': 'phone', 'label': 'Телефон', 'type': 'str', 'required': True, 'maxlen': 30},
            {'name': 'email', 'label': 'Email', 'type': 'str', 'required': False},
        ]
    },
    'organization_tour_agency': {
        'pk': 'organization_id',
        'fields': [
            {'name': 'organization_id', 'label': 'Организация', 'type': 'fk', 'ref_table': 'organization', 'display_col': 'name', 'required': True},
            {'name': 'license_number', 'label': 'Номер лицензии', 'type': 'str', 'required': True},
            {'name': 'country', 'label': 'Страна', 'type': 'str', 'required': False},
        ]
    },
    'organization_event_organizer': {
        'pk': 'organization_id',
        'fields': [
            {'name': 'organization_id', 'label': 'Организация', 'type': 'fk', 'ref_table': 'organization', 'display_col': 'name', 'required': True},
            {'name': 'profile', 'label': 'Профиль мероприятий', 'type': 'str', 'required': True, 'maxlen': 100},
            {'name': 'contact_person', 'label': 'Контактное лицо', 'type': 'str', 'required': False, 'maxlen': 200},
        ]
    },
    'contract': {
        'pk': 'contract_id',
        'fields': [
            {'name': 'contract_id', 'label': 'ID', 'type': 'int', 'editable': False},
            {'name': 'contract_number', 'label': 'Номер договора', 'type': 'str', 'required': True},
            {'name': 'organization_id', 'label': 'Организация', 'type': 'fk', 'ref_table': 'organization', 'display_col': 'name', 'required': True},
            {'name': 'signed_on', 'label': 'Дата подписания', 'type': 'date', 'required': True},
            {'name': 'valid_from', 'label': 'Действует с', 'type': 'date', 'required': True},
            {'name': 'valid_to', 'label': 'Действует по', 'type': 'date', 'required': True},
            {'name': 'discount_percent', 'label': 'Скидка (%)', 'type': 'numeric', 'required': True, 'min': 0, 'max': 100},
        ]
    },
    'client': {
        'pk': 'client_id',
        'fields': [
            {'name': 'client_id', 'label': 'ID', 'type': 'int', 'editable': False},
            {'name': 'first_name', 'label': 'Имя', 'type': 'str', 'required': True, 'maxlen': 200},
            {'name': 'last_name', 'label': 'Фамилия', 'type': 'str', 'required': True, 'maxlen': 200},
            {'name': 'birth_date', 'label': 'Дата рождения', 'type': 'date', 'required': False},
            {'name': 'passport_number', 'label': 'Паспорт', 'type': 'str', 'required': True},
            {'name': 'phone', 'label': 'Телефон', 'type': 'str', 'required': True},
            {'name': 'email', 'label': 'Email', 'type': 'str', 'required': False},
            {'name': 'created_at', 'label': 'Дата регистрации', 'type': 'timestamp', 'editable': False},
        ]
    },
    'booking': {
        'pk': 'booking_id',
        'fields': [
            {'name': 'booking_id', 'label': 'ID', 'type': 'int', 'editable': False},
            {'name': 'contract_id', 'label': 'Договор', 'type': 'fk', 'ref_table': 'contract', 'display_col': 'contract_number', 'required': False},
            {'name': 'client_id', 'label': 'Ответственный клиент', 'type': 'fk', 'ref_table': 'client', 'display_col': 'last_name', 'required': False},
            {'name': 'created_at', 'label': 'Создана', 'type': 'timestamp', 'editable': False},
            {'name': 'planned_checkin', 'label': 'Заезд план', 'type': 'date', 'required': True},
            {'name': 'planned_checkout', 'label': 'Выезд план', 'type': 'date', 'required': True},
            {'name': 'requested_stars', 'label': 'Запрошенная звёздность', 'type': 'int', 'required': True, 'min': 2, 'max': 5},
            {'name': 'requested_floor', 'label': 'Желаемый этаж', 'type': 'int', 'required': False, 'min': 1},
            {'name': 'rooms_count', 'label': 'Кол-во номеров', 'type': 'int', 'required': True, 'min': 1},
            {'name': 'people_count', 'label': 'Кол-во людей', 'type': 'int', 'required': True, 'min': 1},
            {'name': 'keep_on_same_floor', 'label': 'Селять на одном этаже', 'type': 'bool', 'required': True},
            {'name': 'status', 'label': 'Статус', 'type': 'str', 'required': True, 'choices': ['ACTIVE', 'CANCELLED', 'FULFILLED', 'NO_SHOW']},
            {'name': 'cancelled_at', 'label': 'Дата отмены', 'type': 'timestamp', 'editable': False},
            {'name': 'cancellation_fee', 'label': 'Штраф за отмену', 'type': 'numeric', 'editable': False},
        ]
    },
    'booking_room': {
        'pk': None,
        'fields': [
            {'name': 'booking_id', 'label': 'Бронь', 'type': 'fk', 'ref_table': 'booking', 'display_col': 'booking_id', 'required': True},
            {'name': 'room_id', 'label': 'Номер', 'type': 'fk', 'ref_table': 'room', 'display_col': 'room_number', 'required': True},
        ]
    },
    'booking_client': {
        'pk': None,
        'fields': [
            {'name': 'booking_id', 'label': 'Бронь', 'type': 'fk', 'ref_table': 'booking', 'display_col': 'booking_id', 'required': True},
            {'name': 'guest_no', 'label': '№ гостя', 'type': 'int', 'required': True, 'min': 1},
            {'name': 'client_id', 'label': 'Клиент', 'type': 'fk', 'ref_table': 'client', 'display_col': 'last_name', 'required': True},
        ]
    },
    'stay': {
        'pk': 'stay_id',
        'fields': [
            {'name': 'stay_id', 'label': 'ID', 'type': 'int', 'editable': False},
            {'name': 'room_id', 'label': 'Номер', 'type': 'fk', 'ref_table': 'room', 'display_col': 'room_number', 'required': True},
            {'name': 'booking_id', 'label': 'Бронь', 'type': 'fk', 'ref_table': 'booking', 'display_col': 'booking_id', 'required': False},
            {'name': 'checkin_at', 'label': 'Заезд факт', 'type': 'timestamp', 'required': True},
            {'name': 'checkout_at', 'label': 'Выезд факт', 'type': 'timestamp', 'required': False},
        ]
    },
    'stay_client': {
        'pk': None,
        'fields': [
            {'name': 'stay_id', 'label': 'Проживание', 'type': 'fk', 'ref_table': 'stay', 'display_col': 'stay_id', 'required': True},
            {'name': 'client_id', 'label': 'Клиент', 'type': 'fk', 'ref_table': 'client', 'display_col': 'last_name', 'required': True},
        ]
    },
    'room_tariff': {
        'pk': 'tariff_id',
        'fields': [
            {'name': 'tariff_id', 'label': 'ID', 'type': 'int', 'editable': False},
            {'name': 'building_type_id', 'label': 'Тип корпуса', 'type': 'fk', 'ref_table': 'building_type', 'display_col': 'name', 'required': True},
            {'name': 'room_type_id', 'label': 'Тип номера', 'type': 'fk', 'ref_table': 'room_type', 'display_col': 'name', 'required': True},
            {'name': 'price_per_night', 'label': 'Цена за ночь', 'type': 'numeric', 'required': True, 'min': 0},
        ]
    },
    'service_usage': {
        'pk': 'usage_id',
        'fields': [
            {'name': 'usage_id', 'label': 'ID', 'type': 'int', 'editable': False},
            {'name': 'stay_id', 'label': 'Проживание', 'type': 'fk', 'ref_table': 'stay', 'display_col': 'stay_id', 'required': True},
            {'name': 'service_type_id', 'label': 'Услуга', 'type': 'fk', 'ref_table': 'service_type', 'display_col': 'name', 'required': True},
            {'name': 'used_at', 'label': 'Дата использования', 'type': 'timestamp', 'required': True},
            {'name': 'quantity', 'label': 'Количество', 'type': 'numeric', 'required': True, 'min': 0},
        ]
    },
    'invoice': {
        'pk': 'invoice_id',
        'fields': [
            {'name': 'invoice_id', 'label': 'ID', 'type': 'int', 'editable': False},
            {'name': 'created_at', 'label': 'Создан', 'type': 'timestamp', 'editable': False},
            {'name': 'status', 'label': 'Статус', 'type': 'str', 'required': True, 'choices': ['OPEN', 'PARTIALLY_PAID', 'PAID', 'CANCELLED']},
            {'name': 'stay_id', 'label': 'Проживание', 'type': 'fk', 'ref_table': 'stay', 'display_col': 'stay_id', 'required': False},
            {'name': 'booking_id', 'label': 'Бронь (штраф)', 'type': 'fk', 'ref_table': 'booking', 'display_col': 'booking_id', 'required': False},
            {'name': 'client_id', 'label': 'Клиент (штраф)', 'type': 'fk', 'ref_table': 'client', 'display_col': 'last_name', 'required': False},
            {'name': 'room_amount', 'label': 'Сумма проживания', 'type': 'numeric', 'editable': False, 'min': 0},
            {'name': 'service_amount', 'label': 'Сумма услуг', 'type': 'numeric', 'editable': False, 'min': 0},
            {'name': 'penalty_amount', 'label': 'Штрафы', 'type': 'numeric', 'editable': False, 'min': 0},
        ]
    },
    'penalty': {
        'pk': 'penalty_id',
        'fields': [
            {'name': 'penalty_id', 'label': 'ID', 'type': 'int', 'editable': False},
            {'name': 'stay_id', 'label': 'Проживание', 'type': 'fk', 'ref_table': 'stay', 'display_col': 'stay_id', 'required': True},
            {'name': 'description', 'label': 'Описание', 'type': 'str', 'required': False},
            {'name': 'amount', 'label': 'Сумма', 'type': 'numeric', 'required': True, 'min': 0},
            {'name': 'created_at', 'label': 'Дата', 'type': 'timestamp', 'editable': False},
        ]
    },
    'financial_penalty': {
        'pk': 'penalty_id',
        'fields': [
            {'name': 'penalty_id', 'label': 'ID', 'type': 'int', 'editable': False},
            {'name': 'amount', 'label': 'Сумма', 'type': 'numeric', 'required': True, 'min': 0},
            {'name': 'reason', 'label': 'Причина', 'type': 'text', 'required': True},
            {'name': 'created_at', 'label': 'Дата создания', 'type': 'timestamp', 'editable': False},
            {'name': 'client_id', 'label': 'Клиент', 'type': 'fk', 'ref_table': 'client', 'display_col': 'last_name', 'required': False},
            {'name': 'organization_id', 'label': 'Организация', 'type': 'fk', 'ref_table': 'organization', 'display_col': 'name', 'required': False},
            {'name': 'booking_id', 'label': 'Бронь', 'type': 'fk', 'ref_table': 'booking', 'display_col': 'booking_id', 'required': True},
            {'name': 'invoice_id', 'label': 'Счёт', 'type': 'fk', 'ref_table': 'invoice', 'display_col': 'invoice_id', 'required': False},
            {'name': 'created_by', 'label': 'Кем создано', 'type': 'str', 'required': True},
        ]
    },
    'payment': {
        'pk': 'payment_id',
        'fields': [
            {'name': 'payment_id', 'label': 'ID', 'type': 'int', 'editable': False},
            {'name': 'invoice_id', 'label': 'Счёт', 'type': 'fk', 'ref_table': 'invoice', 'display_col': 'invoice_id', 'required': True},
            {'name': 'paid_at', 'label': 'Дата оплаты', 'type': 'timestamp', 'required': True},
            {'name': 'amount', 'label': 'Сумма', 'type': 'numeric', 'required': True, 'min': 0},
            {'name': 'method', 'label': 'Способ', 'type': 'str', 'required': True, 'choices': ['CASH', 'CARD', 'TRANSFER', 'OTHER']},
        ]
    },
    'complaint': {
        'pk': 'complaint_id',
        'fields': [
            {'name': 'complaint_id', 'label': 'ID', 'type': 'int', 'editable': False},
            {'name': 'client_id', 'label': 'Клиент', 'type': 'fk', 'ref_table': 'client', 'display_col': 'last_name', 'required': True},
            {'name': 'submitted_at', 'label': 'Дата подачи', 'type': 'timestamp', 'editable': False},
            {'name': 'text', 'label': 'Текст жалобы', 'type': 'text', 'required': True},
            {'name': 'status', 'label': 'Статус', 'type': 'str', 'required': True, 'choices': ['NEW', 'IN_PROGRESS', 'CLOSED']},
            {'name': 'resolution', 'label': 'Решение', 'type': 'text', 'required': False},
        ]
    },
    'review': {
        'pk': 'review_id',
        'fields': [
            {'name': 'review_id', 'label': 'ID', 'type': 'int', 'editable': False},
            {'name': 'client_id', 'label': 'Клиент', 'type': 'fk', 'ref_table': 'client', 'display_col': 'last_name', 'required': True},
            {'name': 'review_date', 'label': 'Дата отзыва', 'type': 'timestamp', 'editable': False},
            {'name': 'text', 'label': 'Текст', 'type': 'text', 'required': False},
            {'name': 'service_score', 'label': 'Оценка сервиса (1-5)', 'type': 'int', 'required': True, 'min': 1, 'max': 5},
            {'name': 'price_score', 'label': 'Оценка цены (1-5)', 'type': 'int', 'required': True, 'min': 1, 'max': 5},
        ]
    },
    'expense': {
        'pk': 'expense_id',
        'fields': [
            {'name': 'expense_id', 'label': 'ID', 'type': 'int', 'editable': False},
            {'name': 'expense_date', 'label': 'Дата расхода', 'type': 'date', 'required': True},
            {'name': 'amount', 'label': 'Сумма', 'type': 'numeric', 'required': True, 'min': 0},
            {'name': 'description', 'label': 'Описание', 'type': 'str', 'required': False},
            {'name': 'building_id', 'label': 'Корпус', 'type': 'fk', 'ref_table': 'building', 'display_col': 'name', 'required': False},
        ]
    },
}