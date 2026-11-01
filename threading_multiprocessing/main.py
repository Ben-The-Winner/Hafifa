import warnings
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import logging
from functools import partial

import pandas as pd
import yfinance as yf
from pandas.errors import Pandas4Warning

from Settings import (
    BASE_DIR,
    DESTINATION_FILE,
    MAX_WORKERS,
    STOCKS,
)

warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=Pandas4Warning)
logger = logging.getLogger(__name__)


def load_hours(file_path: str | Path) -> list[str]:
    path = Path(file_path)
    if not path.is_absolute():
        path = BASE_DIR / path

    if not path.exists():
        logger.error(f"Dates file not found: {path}")
        return []

    with open(path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def fetch_hour_data(hour: str, stock_initials: str) -> pd.Series | None:
    date_time = pd.to_datetime(hour)

    start_date = date_time.strftime("%Y-%m-%d")
    end_date = (date_time + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    ticker = yf.Ticker(stock_initials)
    data = ticker.history(
        start=start_date,
        end=end_date,
        interval="1h",
    )

    if data.empty:
        return None

    target_hour = date_time.strftime("%Y-%m-%d %H:00:00")
    matching_rows = data[
        data.index.strftime("%Y-%m-%d %H:00:00") == target_hour
    ]

    if matching_rows.empty:
        return None

    return matching_rows.iloc[0]


def calculate_percentage_change(open_price: float, close_price: float) -> float:
    return round(((close_price - open_price) / open_price) * 100, 4)


def process_hour(hour: str, stock_type: str, stock_initials: str) -> dict | None:
    try:
        row = fetch_hour_data(hour, stock_initials)

        if row is None:
            logger.error(f"No data found for hour: {hour} ({stock_type})")
            return None

        percentage_change = calculate_percentage_change(
            row["Open"],
            row["Close"],
        )

        return {
            "hour": hour,
            "stock type": stock_type,
            "percentage change": percentage_change,
        }

    except Exception as error:
        logger.error(f"Error processing hour {hour} for {stock_type}: {error}")
        return None


def process_multiple_hours(
    hours: list[str], stock_type: str, stock_initials: str
) -> list[dict]:
    results = []

    logger.info(
        f"Processing {len(hours)} hours for {stock_type} using ThreadPoolExecutor..."
    )

    worker_func = partial(
        process_hour, stock_type=stock_type, stock_initials=stock_initials
    )

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for result in executor.map(worker_func, hours):
            if result is not None:
                results.append(result)

    return results


def save_results(results: list[dict], destination: str) -> None:
    if not results:
        logger.error("No valid results to write.")
        return

    output = pd.DataFrame(results)
    output = output[["hour", "stock type", "percentage change"]]
    output.to_csv(destination, index=False)

    logger.info(f"Results successfully written to {destination}")


def main() -> None:
    all_results = []

    for stock_type, stock_initials, dates_file in STOCKS:
        hours_list = load_hours(dates_file)

        if not hours_list:
            logger.error(f"No hours found to process in file: {dates_file}. Skipping.")
            continue

        company_results = process_multiple_hours(
            hours_list, stock_type, stock_initials
        )
        all_results.extend(company_results)

    save_results(all_results, DESTINATION_FILE)


if __name__ == "__main__":
    main()
