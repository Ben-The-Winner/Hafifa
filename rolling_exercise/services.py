import pandas as pd
import calculate_aqi
from database import get_connection


def process_and_save_csv(file_file):
  try:
    df = pd.read_csv(file_file)
  except Exception as e:
    raise ValueError(f"Failed to parse CSV file: {str(e)}")

  required_columns = ["date", "city", "pm25", "no2", "co2"]
  for col in required_columns:
    if col not in df.columns:
      raise ValueError(f"Missing required column in CSV: {col}")

  conn = get_connection()
  cursor = conn.cursor()

  inserted_rows = 0
  alerts_count = 0

  for _, row in df.iterrows():
    if (
        pd.isna(row["date"])
        or pd.isna(row["city"])
        or pd.isna(row["pm25"])
        or pd.isna(row["no2"])
        or pd.isna(row["co2"])
    ):
      continue

    date_str = str(row["date"])
    city_name = str(row["city"])
    pm25 = float(row["pm25"])
    no2 = float(row["no2"])
    co2 = float(row["co2"])

    try:
      aqi_value, aqi_level = calculate_aqi(pm25, no2, co2)
    except Exception:
      continue

    cursor.execute(
        """
            INSERT INTO measurements (date, city, pm25, no2, co2, aqi, aqi_level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            date_str,
            city_name,
            pm25,
            no2,
            co2,
            float(aqi_value),
            str(aqi_level),
        ),
    )
    inserted_rows += 1

    if aqi_value > 300:
      cursor.execute(
          """
                INSERT INTO alerts (date, city, aqi)
                VALUES (?, ?, ?)
            """,
          (date_str, city_name, float(aqi_value)),
      )
      alerts_count += 1

  conn.commit()
  conn.close()

  return inserted_rows, alerts_count