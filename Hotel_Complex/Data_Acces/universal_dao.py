import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import psycopg2
import psycopg2.extras
from db_connection import DatabaseConnection


class UniversalDAO:
    """Универсальный CRUD для любой таблицы."""

    @staticmethod
    def get_all(table_name, limit=100, offset=0, order_by=None):
        sql = f"SELECT * FROM {table_name}"
        if order_by:
            sql += f" ORDER BY {order_by}"
        sql += " LIMIT %s OFFSET %s"
        with DatabaseConnection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(sql, (limit, offset))
                rows = cur.fetchall()
                return [dict(row) for row in rows]

    @staticmethod
    def get_by_id(table_name, pk_name, pk_value):
        sql = f"SELECT * FROM {table_name} WHERE {pk_name} = %s"
        with DatabaseConnection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(sql, (pk_value,))
                row = cur.fetchone()
                return dict(row) if row else None

    @staticmethod
    def insert(table_name, data):
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) RETURNING *"
        with DatabaseConnection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(sql, tuple(data.values()))
                conn.commit()
                inserted_row = cur.fetchone()
                return dict(inserted_row)

    @staticmethod
    def update(table_name, pk_name, pk_value, data):
        set_clause = ', '.join([f"{k}=%s" for k in data.keys()])
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {pk_name}=%s RETURNING *"
        params = tuple(data.values()) + (pk_value,)
        with DatabaseConnection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(sql, params)
                conn.commit()
                updated_row = cur.fetchone()
                return dict(updated_row) if updated_row else None

    @staticmethod
    def delete(table_name, pk_name, pk_value):
        sql = f"DELETE FROM {table_name} WHERE {pk_name}=%s"
        with DatabaseConnection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (pk_value,))
                conn.commit()
                return cur.rowcount > 0

    @staticmethod
    def get_fk_options(ref_table, display_col, id_col=None):
        if id_col is None:
            id_col = f"{ref_table}_id"
        sql = f"SELECT {id_col}, {display_col} FROM {ref_table} ORDER BY {display_col}"
        with DatabaseConnection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                return [(row[0], row[1]) for row in rows]

    @staticmethod
    def get_all_paginated(table_name, page=1, per_page=50, order_by=None):
        """Получить записи таблицы с пагинацией.

        Returns:
            dict: {
                'records': [...],      # Список записей
                'page': int,           # Текущая страница
                'per_page': int,       # Записей на странице
                'total': int,          # Всего записей
                'total_pages': int     # Всего страниц
            }
        """

        count_sql = f"SELECT COUNT(*) FROM {table_name}"

        offset = (page - 1) * per_page

        sql = f"SELECT * FROM {table_name}"
        if order_by:
            sql += f" ORDER BY {order_by}"
        else:
            sql += f" ORDER BY 1"

        sql += f" LIMIT %s OFFSET %s"

        with DatabaseConnection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:

                cur.execute(count_sql)
                total = cur.fetchone()[0]

                cur.execute(sql, (per_page, offset))
                records = [dict(row) for row in cur.fetchall()]

                total_pages = max(1, (total + per_page - 1) // per_page)

                return {
                    'records': records,
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'total_pages': total_pages
                }

    @staticmethod
    def get_filtered_paginated(table_name, filters=None, page=1, per_page=50, order_by=None):
        offset = (page - 1) * per_page

        where_clause = ""
        params = []

        if filters:
            conditions = []
            for col, val in filters.items():
                conditions.append(f"{col} = %s")
                params.append(val)
            where_clause = "WHERE " + " AND ".join(conditions)

        count_sql = f"SELECT COUNT(*) FROM {table_name} {where_clause}"

        sql = f"SELECT * FROM {table_name} {where_clause}"
        if order_by:
            sql += f" ORDER BY {order_by}"
        else:
            sql += " ORDER BY 1"

        sql += " LIMIT %s OFFSET %s"

        with DatabaseConnection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(count_sql, params)
                total = cur.fetchone()[0]

                page_params = params + [per_page, offset]
                cur.execute(sql, page_params)
                records = [dict(row) for row in cur.fetchall()]

                total_pages = max(1, (total + per_page - 1) // per_page)

                return {
                    'records': records,
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'total_pages': total_pages
                }