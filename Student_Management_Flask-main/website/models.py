import os
import mysql.connector
from mysql.connector import Error as MySQLError

# Doc cau hinh tu bien moi truong (tien cho dev va prod)
# Theo yeu cau, mac dinh su dung port 3306. Co the override bang DB_PORT env var.
DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_PORT = int(os.environ.get("DB_PORT", "3306"))
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "Hoangduy01062005")
DB_NAME = os.environ.get("DB_NAME", "sinhvien")


def get_conn():
    """Return a new MySQL connection. Raises RuntimeError with details on failure.

    Note: we return a fresh connection per call to avoid sharing a single
    connection object across requests and to defer connection attempts until
    first use (avoids import-time failures).
    """
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            connection_timeout=5,
        )
        return conn
    except MySQLError as err:
        msg = (
            f"[models.py] Khong the ket noi MySQL tai {DB_HOST}:{DB_PORT} voi user={DB_USER} db={DB_NAME}."
            f"\nLoi tu connector: {err}"
        )
        raise RuntimeError(msg)
