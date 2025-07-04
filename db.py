from psycopg2 import connect
from logger import logger

DB_PARAMS = {
    "dbname": "session",
    "user": "postgres",
    "password": "1212",
    "host": "localhost",
    "port": 5432,
}


def get_connection():
    try:
        conn = connect(**DB_PARAMS)
        logger.info("Подключение к базе данных успешно")
        return conn
    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        raise
