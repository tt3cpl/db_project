import psycopg2
from psycopg2 import sql
from logger import logger

DB_PARAMS = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "Goshapes12!",
    "host": "localhost",
    "port": 5432,
}


def get_connection():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        logger.info("Подключение к базе данных успешно")
        return conn
    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        raise
