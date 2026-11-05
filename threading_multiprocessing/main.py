import warnings
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import logging
from functools import partial

import pandas as pd
import yfinance as yf

from configurations import (
    BASE_DIR,
    DESTINATION_FILE,
    MAX_WORKERS,
    STOCKS,
)

logger = logging.getLogger(__name__)


def load_hours(file_path: str | Path) -> list[str]:
    path = Path(file_path)

    if not path.is_absolute():
        path = BASE_DIR / path

    if not path.exists():
        raise FileNotFoundError(f"Critical dates file not found: {path}")

    with open(path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def fetch_stock_data(hours: list[str], stock_initials: str) -> pd.DataFrame | None:
    try:
        date_times = pd.to_datetime(hours)
        start_date = date_times.min().strftime("%Y-%m-%d")
        end_date = (
                date_times.max() + pd.Timedelta(days=1)
        ).strftime("%Y-%m-%d")

        ticker = yf.Ticker(stock_initials)

        data = ticker.history(
            start=start_date,
            end=end_date,
            interval="1h",
        )

        if data.empty:
            logger.error(f"No data returned for {stock_initials}")
            return None

        return data

    except Exception as error:
        logger.exception(
            f"Error fetching data for {stock_initials}: {error}"
        )
        return None


def calculate_percentage_change(open_price: float, close_price: float) -> float:
    if open_price == 0:
        raise ValueError("Open price cannot be zero")
    return round(((close_price - open_price) / open_price) * 100, 4)


def convert_to_new_york_time(hour: str) -> pd.Timestamp:
    date_time = pd.Timestamp(hour)

    if date_time.tzinfo is None:
        return date_time.tz_localize("America/New_York")

    return date_time.tz_convert("America/New_York")


def find_matching_candle(date_time: pd.Timestamp, stock_data: pd.DataFrame, ) -> pd.Series | None:
    matching_rows = stock_data[(stock_data.index <= date_time) & (stock_data.index + pd.Timedelta(hours=1) > date_time)]

    if matching_rows.empty:
        return None

    return matching_rows.iloc[-1]


def extract_prices_from_a_candle(candle: pd.Series) -> tuple[float, float]:
    return candle["Open"], candle["Close"]


def create_hour_result(hour: str, stock_type: str, open_price: float, close_price: float, ) -> dict:
    percentage_change = calculate_percentage_change(open_price, close_price, )

    return {
        "hour": hour,
        "stock type": stock_type,
        "percentage change": percentage_change,
    }


def process_hour(hour: str, stock_type: str, stock_data: pd.DataFrame, ) -> dict | None:
    try:
        if stock_data.empty:
            return None

        date_time = convert_to_new_york_time(hour)

        candle = find_matching_candle(date_time, stock_data)

        if candle is None:
            logger.warning(
                f"No Matching found for hour: {hour} ({stock_type})"
            )
            return None

        open_price, close_price = extract_prices_from_a_candle(candle)

        return create_hour_result(
            hour,
            stock_type,
            open_price,
            close_price,
        )

    except (KeyError, IndexError, ValueError) as error:
        logger.error(
            f"Data error processing hour {hour} for {stock_type}: {error}"
        )
        return None


def save_results(results: list[dict], destination: str | Path) -> None:
    if not results:
        logger.error("No valid results to write.")
        return

    output = pd.DataFrame(results)

    output = output[
        ["hour", "stock type", "percentage change"]
    ]

    output.to_csv(destination, index=False)

    logger.info(
        f"Results successfully written to {destination}"
    )


def process_stock(hours: list[str], stock_type: str, stock_initials: str) -> list[dict]:
    stock_data = fetch_stock_data(hours, stock_initials)

    if stock_data is None:
        return []

    worker_func = partial(
        process_hour,
        stock_type=stock_type,
        stock_data=stock_data,
    )

    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for result in executor.map(worker_func, hours):
            if result is not None:
                results.append(result)

    return results


def main() -> None:
    all_results = []

    for stock_type, stock_initials, dates_file in STOCKS:

        hours_list = load_hours(dates_file)

        if not hours_list:
            logger.error(
                f"No hours found to process in file: {dates_file}. Skipping."
            )
            continue

        company_results = process_stock(
            hours_list,
            stock_type,
            stock_initials,
        )

        all_results.extend(company_results)

    save_results(all_results, DESTINATION_FILE)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    main()
