import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_connection import DatabaseConnection
import psycopg2.extras


def _run_query(sql, params=None):
    """Вспомогательная функция для выполнения произвольного SQL и возврата всех строк как списка словарей."""
    with DatabaseConnection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, params or ())
            rows = cur.fetchall()
            return [dict(row) for row in rows]


# ----------------------------------------------------------------------
# 1. Фирмы, забронировавшие места в объёме не менее указанного
def get_firms_by_volume(min_people, start_date=None, end_date=None):
    if start_date and end_date:
        sql = """
            SELECT o.organization_id, o.name, SUM(b.people_count) AS total_people
            FROM organization o
            JOIN contract c ON o.organization_id = c.organization_id
            JOIN booking b ON c.contract_id = b.contract_id
            WHERE b.status <> 'CANCELLED'
              AND b.planned_checkin >= %s AND b.planned_checkout <= %s
            GROUP BY o.organization_id, o.name
            HAVING SUM(b.people_count) >= %s
            ORDER BY o.name
        """
        return _run_query(sql, (start_date, end_date, min_people))
    else:
        sql = """
            SELECT o.organization_id, o.name, SUM(b.people_count) AS total_people
            FROM organization o
            JOIN contract c ON o.organization_id = c.organization_id
            JOIN booking b ON c.contract_id = b.contract_id
            WHERE b.status <> 'CANCELLED'
            GROUP BY o.organization_id, o.name
            HAVING SUM(b.people_count) >= %s
            ORDER BY o.name
        """
        return _run_query(sql, (min_people,))


def get_firms_count_by_volume(min_people, start_date, end_date):
    sql = """
        WITH organizations_with_bookings AS (
            SELECT o.organization_id
            FROM organization o
            JOIN contract c ON o.organization_id = c.organization_id
            JOIN booking b ON c.contract_id = b.contract_id
            WHERE b.status <> 'CANCELLED'
              AND b.planned_checkin < %s AND b.planned_checkout > %s
            GROUP BY o.organization_id
            HAVING SUM(b.people_count) >= %s
        )
        SELECT COUNT(*) AS organizations_count
        FROM organizations_with_bookings
    """
    res = _run_query(sql, (end_date, start_date, min_people))
    return res[0]['organizations_count'] if res else 0


# ----------------------------------------------------------------------
# 2. Постояльцы, заселявшиеся в номера с указанными характеристиками за период
def get_guests_by_room_features(stars, min_capacity, start_date, end_date):
    sql = """
        WITH unique_clients AS (
            SELECT DISTINCT c.client_id, c.first_name, c.last_name
            FROM stay s
            JOIN stay_client sc ON s.stay_id = sc.stay_id
            JOIN client c ON sc.client_id = c.client_id
            JOIN room r ON s.room_id = r.room_id
            JOIN building b ON r.building_id = b.building_id
            JOIN building_type bt ON b.building_type_id = bt.building_type_id
            JOIN room_type rt ON r.room_type_id = rt.room_type_id
            WHERE bt.hotel_stars = %s AND rt.capacity >= %s
              AND s.checkin_at >= %s AND s.checkin_at <= %s
        )
        SELECT client_id, first_name, last_name,
               COUNT(*) OVER() AS total_clients
        FROM unique_clients
        ORDER BY client_id
    """
    return _run_query(sql, (stars, min_capacity, start_date, end_date))


# ----------------------------------------------------------------------
# 3. Количество свободных номеров на данный момент
def get_free_rooms_count():
    sql = """
        SELECT COUNT(*) AS free_rooms_count
        FROM room r
        WHERE NOT EXISTS (
            SELECT 1 FROM stay s
            WHERE s.room_id = r.room_id
              AND s.checkin_at <= NOW()
              AND (s.checkout_at IS NULL OR s.checkout_at > NOW())
        ) AND NOT EXISTS (
            SELECT 1 FROM booking_room br
            JOIN booking b ON b.booking_id = br.booking_id
            WHERE br.room_id = r.room_id
              AND b.status = 'ACTIVE'
              AND b.planned_checkin <= CURRENT_DATE
              AND b.planned_checkout > CURRENT_DATE
        )
    """
    res = _run_query(sql)
    return res[0]['free_rooms_count'] if res else 0


# ----------------------------------------------------------------------
# 4. Количество свободных номеров с указанными характеристиками на заданный момент
def get_free_rooms_by_features(stars, min_capacity, moment):
    sql = """
        SELECT COUNT(*) AS free_rooms_count
        FROM room r
        JOIN building b ON r.building_id = b.building_id
        JOIN building_type bt ON b.building_type_id = bt.building_type_id
        JOIN room_type rt ON r.room_type_id = rt.room_type_id
        WHERE bt.hotel_stars = %s AND rt.capacity >= %s
          AND NOT EXISTS (
              SELECT 1 FROM stay s
              WHERE s.room_id = r.room_id
                AND s.checkin_at <= %s
                AND (s.checkout_at IS NULL OR s.checkout_at > %s)
          )
          AND NOT EXISTS (
              SELECT 1 FROM booking_room br
              JOIN booking bk ON bk.booking_id = br.booking_id
              WHERE br.room_id = r.room_id
                AND bk.status = 'ACTIVE'
                AND bk.planned_checkin <= %s::date
                AND bk.planned_checkout > %s::date
          )
    """
    res = _run_query(sql, (stars, min_capacity, moment, moment, moment, moment))
    return res[0]['free_rooms_count'] if res else 0


# ----------------------------------------------------------------------
# 5. Сведения о конкретном номере (свободен ли, ближайшая занятость, характеристики)
def get_room_free_info(room_id):
    sql = """
        SELECT 
            r.room_number, r.floor_no, b.name AS building,
            bt.hotel_stars, rt.name AS room_type, rt.capacity, t.price_per_night,
            NOT EXISTS (
                SELECT 1 FROM stay s
                WHERE s.room_id = r.room_id
                  AND s.checkin_at <= NOW()
                  AND (s.checkout_at IS NULL OR s.checkout_at > NOW())
            ) AS is_free_now,
            LEAST(
                COALESCE((SELECT MIN(s.checkin_at) FROM stay s 
                          WHERE s.room_id = r.room_id AND s.checkin_at > NOW()),
                         'infinity'::timestamp),
                COALESCE((SELECT MIN(b.planned_checkin) FROM booking_room br
                          JOIN booking b ON br.booking_id = b.booking_id
                          WHERE br.room_id = r.room_id 
                            AND b.status = 'ACTIVE' 
                            AND b.planned_checkin > NOW()),
                         'infinity'::timestamp)
            ) AS next_occupancy_start
        FROM room r
        JOIN building b ON r.building_id = b.building_id
        JOIN building_type bt ON b.building_type_id = bt.building_type_id
        JOIN room_type rt ON r.room_type_id = rt.room_type_id
        JOIN room_tariff t ON bt.building_type_id = t.building_type_id 
                           AND rt.room_type_id = t.room_type_id
        WHERE r.room_id = %s
    """
    res = _run_query(sql, (room_id,))
    return res[0] if res else None


# ----------------------------------------------------------------------
# 6. Занятые сейчас номера, освобождающиеся к указанному сроку
def get_occupied_rooms_free_by_deadline(reference_ts, deadline_ts):
    sql = """
        SELECT 
            r.room_id, r.room_number, r.floor_no AS floor,
            b.name AS building, bt.hotel_stars,
            rt.name AS room_type, rt.capacity,
            s.checkin_at,
            COALESCE(s.checkout_at, bk.planned_checkout::timestamp) AS checkout_time,
            ROUND(EXTRACT(EPOCH FROM (COALESCE(s.checkout_at, bk.planned_checkout::timestamp) - %s)) / 3600, 1) AS hours_until_free
        FROM stay s
        JOIN room r ON s.room_id = r.room_id
        JOIN building b ON r.building_id = b.building_id
        JOIN building_type bt ON b.building_type_id = bt.building_type_id
        JOIN room_type rt ON r.room_type_id = rt.room_type_id
        LEFT JOIN booking bk ON s.booking_id = bk.booking_id
        WHERE s.checkin_at <= %s
          AND (s.checkout_at IS NULL OR s.checkout_at > %s)
          AND COALESCE(s.checkout_at, bk.planned_checkout::timestamp) IS NOT NULL
          AND COALESCE(s.checkout_at, bk.planned_checkout::timestamp) > %s
          AND COALESCE(s.checkout_at, bk.planned_checkout::timestamp) <= %s
        ORDER BY checkout_time
    """
    return _run_query(sql, (reference_ts, reference_ts, reference_ts, reference_ts, deadline_ts))


# ----------------------------------------------------------------------
# 7. Объём бронирования фирмой за период и предпочтения по типам номеров
def get_booking_volume_and_preferences(org_name, start_date, end_date):
    sql_summary = """
        WITH org_bookings AS (
            SELECT b.booking_id, b.rooms_count, b.people_count
            FROM organization o
            JOIN contract c ON o.organization_id = c.organization_id
            JOIN booking b ON c.contract_id = b.contract_id
            WHERE o.name = %s AND b.status <> 'CANCELLED'
              AND b.planned_checkin < %s AND b.planned_checkout > %s
        )
        SELECT COUNT(*) AS bookings_count,
               SUM(rooms_count) AS total_rooms_booked,
               SUM(people_count) AS total_people_booked
        FROM org_bookings
    """
    summary_res = _run_query(sql_summary, (org_name, end_date, start_date))
    summary = summary_res[0] if summary_res else {}

    sql_pref = """
        WITH org_bookings AS (
            SELECT b.booking_id
            FROM organization o
            JOIN contract c ON o.organization_id = c.organization_id
            JOIN booking b ON c.contract_id = b.contract_id
            WHERE o.name = %s AND b.status <> 'CANCELLED'
              AND b.planned_checkin < %s AND b.planned_checkout > %s
        )
        SELECT rt.name AS room_type, COUNT(*) AS times_selected
        FROM org_bookings ob
        JOIN booking_room br ON ob.booking_id = br.booking_id
        JOIN room r ON br.room_id = r.room_id
        JOIN room_type rt ON r.room_type_id = rt.room_type_id
        GROUP BY rt.name
    """
    pref = _run_query(sql_pref, (org_name, end_date, start_date))
    total = sum(item['times_selected'] for item in pref) if pref else 1
    for item in pref:
        item['percentage'] = round(item['times_selected'] * 100.0 / total, 2)
    pref.sort(key=lambda x: x['percentage'], reverse=True)
    return summary, pref


# ----------------------------------------------------------------------
# 8. Список недовольных клиентов и их жалобы
def get_unhappy_clients_with_complaints():
    sql = """
        WITH unhappy_clients AS (
            SELECT client_id FROM complaint
            UNION
            SELECT client_id FROM review WHERE service_score <= 3 OR price_score <= 3
        )
        SELECT c.client_id, c.first_name, c.last_name,
               comp.complaint_id, comp.text, comp.status
        FROM unhappy_clients uc
        JOIN client c ON uc.client_id = c.client_id
        LEFT JOIN complaint comp ON c.client_id = comp.client_id
        ORDER BY c.client_id
    """
    return _run_query(sql)


# ----------------------------------------------------------------------
# 9. Рентабельность корпусов за период
def get_profitability(start_date, end_date):
    sql = """
        WITH sales AS (
            SELECT r.building_id, SUM(i.room_amount) AS room_sales
            FROM invoice i
            JOIN stay s ON s.stay_id = i.stay_id
            JOIN room r ON r.room_id = s.room_id
            WHERE s.checkin_at < %s AND (s.checkout_at IS NULL OR s.checkout_at > %s)
            GROUP BY r.building_id
        ),
        costs AS (
            SELECT e.building_id, SUM(e.amount) AS overhead_costs
            FROM expense e
            WHERE e.building_id IS NOT NULL
              AND e.expense_date >= %s AND e.expense_date < %s
            GROUP BY e.building_id
        )
        SELECT b.building_id, b.name AS building_name,
               COALESCE(s.room_sales, 0) AS room_sales,
               COALESCE(c.overhead_costs, 0) AS overhead_costs,
               CASE WHEN COALESCE(c.overhead_costs, 0) = 0 THEN COALESCE(s.room_sales, 0)
                    ELSE ROUND(COALESCE(s.room_sales, 0) / c.overhead_costs, 2)
               END AS profitability_ratio
        FROM building b
        LEFT JOIN sales s ON s.building_id = b.building_id
        LEFT JOIN costs c ON c.building_id = b.building_id
        ORDER BY b.building_id
    """
    return _run_query(sql, (end_date, start_date, start_date, end_date))


# ----------------------------------------------------------------------
# 10. Сведения о постояльцах из заданного номера (развёрнутый отчёт)
def get_guest_info_by_room(room_id):
    sql = """
        SELECT
            r.room_id, b.name AS building_name, r.room_number,
            c.client_id, c.first_name, c.last_name,
            s.stay_id, s.checkin_at, s.checkout_at,
            COALESCE(i.service_amount, 0) AS service_invoice_amount,
            comp.complaint_id, comp.submitted_at AS complaint_date,
            comp.text AS complaint_text, comp.status AS complaint_status,
            st.service_type_id, st.name AS service_name,
            su.used_at, su.quantity
        FROM room r
        JOIN building b ON b.building_id = r.building_id
        JOIN stay s ON s.room_id = r.room_id
        JOIN stay_client sc ON sc.stay_id = s.stay_id
        JOIN client c ON c.client_id = sc.client_id
        LEFT JOIN invoice i ON i.stay_id = s.stay_id
        LEFT JOIN complaint comp ON comp.client_id = c.client_id
        LEFT JOIN service_usage su ON su.stay_id = s.stay_id
        LEFT JOIN service_type st ON st.service_type_id = su.service_type_id
        WHERE r.room_id = %s
        ORDER BY c.client_id, s.checkin_at, su.used_at, comp.submitted_at
    """
    return _run_query(sql, (room_id,))


# ----------------------------------------------------------------------
# 11. Фирмы с действующими договорами в указанный период
def get_firms_with_contracts_period(start_date, end_date):
    sql = """
        SELECT DISTINCT
            o.organization_id, o.name, o.phone, o.email,
            c.contract_number, c.valid_from, c.valid_to
        FROM contract c
        JOIN organization o ON o.organization_id = c.organization_id
        WHERE c.valid_from <= %s AND c.valid_to >= %s
        ORDER BY o.name
    """
    return _run_query(sql, (end_date, start_date))


# ----------------------------------------------------------------------
# 12. Наиболее частые посетители (по всем корпусам или по одному)
def get_frequent_guests_all():
    sql = """
        SELECT
            c.client_id, c.first_name, c.last_name,
            COUNT(DISTINCT sc.stay_id) AS visits_count,
            COUNT(DISTINCT r.building_id) AS buildings_visited,
            MIN(s.checkin_at) AS first_visit,
            MAX(COALESCE(s.checkout_at, s.checkin_at)) AS last_visit
        FROM client c
        JOIN stay_client sc ON sc.client_id = c.client_id
        JOIN stay s ON s.stay_id = sc.stay_id
        JOIN room r ON r.room_id = s.room_id
        LEFT JOIN booking bk ON bk.booking_id = s.booking_id
        WHERE bk.booking_id IS NULL OR bk.status <> 'CANCELLED'
        GROUP BY c.client_id, c.first_name, c.last_name
        ORDER BY visits_count DESC, last_visit DESC
    """
    return _run_query(sql)


def get_frequent_guests_by_building(building_id):
    sql = """
        SELECT
            c.client_id, c.first_name, c.last_name,
            b.building_id, b.name AS building_name,
            COUNT(DISTINCT sc.stay_id) AS visits_count,
            MIN(s.checkin_at) AS first_visit,
            MAX(COALESCE(s.checkout_at, s.checkin_at)) AS last_visit
        FROM client c
        JOIN stay_client sc ON sc.client_id = c.client_id
        JOIN stay s ON s.stay_id = sc.stay_id
        JOIN room r ON r.room_id = s.room_id
        JOIN building b ON b.building_id = r.building_id
        LEFT JOIN booking bk ON bk.booking_id = s.booking_id
        WHERE b.building_id = %s
          AND (bk.booking_id IS NULL OR bk.status <> 'CANCELLED')
        GROUP BY c.client_id, c.first_name, c.last_name, b.building_id, b.name
        ORDER BY visits_count DESC, last_visit DESC
    """
    return _run_query(sql, (building_id,))


# ----------------------------------------------------------------------
# 13. Новые клиенты за указанный период
def get_new_clients(start_date, end_date):
    sql = """
        SELECT client_id, first_name, last_name, created_at
        FROM client
        WHERE created_at >= %s AND created_at < %s
        ORDER BY created_at
    """
    return _run_query(sql, (start_date, end_date))


# ----------------------------------------------------------------------
# 14. Полная история клиента (визиты, счета, оплаты)
def get_client_full_history(client_id):
    sql = """
        WITH visits AS (
            SELECT sc.client_id, COUNT(DISTINCT sc.stay_id) AS visits_count
            FROM stay_client sc
            GROUP BY sc.client_id
        )
        SELECT
            c.client_id, c.first_name, c.last_name, v.visits_count,
            b.building_id, b.name AS building_name,
            r.room_id, r.room_number,
            s.stay_id, s.checkin_at, s.checkout_at,
            i.invoice_id, i.created_at AS invoice_created_at,
            i.status AS invoice_status,
            i.room_amount, i.service_amount, i.penalty_amount,
            (i.room_amount + i.service_amount + i.penalty_amount) AS total_invoice_amount,
            p.payment_id, p.paid_at, p.amount AS paid_amount, p.method
        FROM client c
        JOIN visits v ON v.client_id = c.client_id
        JOIN stay_client sc ON sc.client_id = c.client_id
        JOIN stay s ON s.stay_id = sc.stay_id
        JOIN room r ON r.room_id = s.room_id
        JOIN building b ON b.building_id = r.building_id
        LEFT JOIN invoice i ON i.stay_id = s.stay_id
        LEFT JOIN payment p ON p.invoice_id = i.invoice_id
        WHERE c.client_id = %s
        ORDER BY s.checkin_at, i.created_at, p.paid_at
    """
    return _run_query(sql, (client_id,))


# ----------------------------------------------------------------------
# 15. Кто занимал номер в определённый период
def get_room_occupants(room_id, start_ts, end_ts):
    sql = """
        SELECT 
            r.room_id, r.room_number, b.name AS building_name,
            s.stay_id, s.checkin_at, s.checkout_at,
            c.client_id, c.first_name, c.last_name
        FROM stay s
        JOIN room r ON r.room_id = s.room_id
        JOIN building b ON b.building_id = r.building_id
        JOIN stay_client sc ON sc.stay_id = s.stay_id
        JOIN client c ON c.client_id = sc.client_id
        WHERE r.room_id = %s
          AND s.checkin_at < %s
          AND (s.checkout_at IS NULL OR s.checkout_at > %s)
        ORDER BY s.checkin_at, c.last_name, c.first_name
    """
    return _run_query(sql, (room_id, end_ts, start_ts))


# ----------------------------------------------------------------------
# 16. Процентное отношение броней партнёров ко всем броням
def get_partner_booking_percentage():
    sql = """
        SELECT 
            COUNT(*) AS total_bookings,
            COUNT(contract_id) AS partner_bookings,
            ROUND(COUNT(contract_id) * 100.0 / COUNT(*), 2) AS partner_percentage
        FROM booking
    """
    res = _run_query(sql)
    return res[0] if res else {'total_bookings': 0, 'partner_bookings': 0, 'partner_percentage': 0.0}