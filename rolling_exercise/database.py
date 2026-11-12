import sqlite3

DB_NAME = "air_quality.db"


def get_connection():
  return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
  conn = get_connection()
  cursor = conn.cursor()

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            city TEXT,
            pm25 REAL,
            no2 REAL,
            co2 REAL,
            aqi REAL,
            aqi_level TEXT
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            city TEXT,
            aqi REAL
        )
    """)
  conn.commit()
  conn.close()