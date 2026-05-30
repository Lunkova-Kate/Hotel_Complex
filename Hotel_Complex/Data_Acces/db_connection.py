import sys
import os

# Добавляем путь к текущей папке для импорта config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import psycopg2
from psycopg2 import pool
from config import DB_CONFIG

# Создаём пул соединений
connection_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=10,
    **DB_CONFIG
)


def get_connection():
    """Получить соединение из пула"""
    try:
        conn = connection_pool.getconn()
        return conn
    except Exception as e:
        print(f"Ошибка получения соединения: {e}")
        raise


def return_connection(conn):
    """Вернуть соединение в пул"""
    if conn:
        connection_pool.putconn(conn)


class DatabaseConnection:
    """Контекстный менеджер для работы с соединением"""
    def __enter__(self):
        self.conn = get_connection()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        return_connection(self.conn)