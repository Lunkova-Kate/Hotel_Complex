ROLE_TABLES = {
    'admin': {
        'read': '*',
        'write': '*',
        'delete': '*',
    },
    'manager': {
        'read': [
            'client', 'booking', 'booking_room', 'booking_client',
            'stay', 'stay_client', 'service_usage', 'complaint', 'review',
            'building', 'building_type', 'room', 'room_type', 'room_tariff',
            'service_type', 'building_service',
            'organization', 'organization_type', 'contract',
            'invoice', 'payment', 'penalty', 'financial_penalty'
        ],
        'write': [
            'client', 'booking', 'booking_room', 'booking_client',
            'stay', 'stay_client', 'service_usage', 'complaint', 'review',
            'payment', 'penalty'
        ],
        'delete': [
            'booking_room', 'booking_client', 'service_usage'
        ],
    }
}


def get_table_list(role, operation):
    perms = ROLE_TABLES.get(role, {})
    lst = perms.get(operation, [])
    if lst == '*':
        return None
    return set(lst)


def can(role, operation, table_name):
    allowed = get_table_list(role, operation)
    if allowed is None:
        return True
    return table_name in allowed