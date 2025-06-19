import psycopg2
from psycopg2 import sql
from logger import logger

DB_PARAMS = {
<<<<<<< HEAD
    "dbname": "postgres",
    "user": "postgres",
    "password": "Goshapes12!",
    "host": "localhost",
    "port": 5432,
=======
    'dbname': 'session',
    'user': 'postgres',
    'password': '1212',
    'host': 'localhost',
    'port': 5432,
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
}


def get_connection():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        logger.info("Подключение к базе данных успешно")
        return conn
    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        raise
