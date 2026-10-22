import base64
import json
import logging
import os
from pathlib import Path
from typing import Dict, List

from playwright.sync_api import Request, sync_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

WAIT_TIMEOUT_MS = 60000
INPUT_FILE = "urls.input"
OUTPUT_DIR = "output"


def load_urls(file_path: str) -> List[str]:
    path = Path(file_path)
    if not path.exists():
        logger.error(f"Input file not found: {file_path}")
        return []

    with open(path, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]
    return urls


def process_url(browser, url: str, index: int) -> None:
    folder = Path(OUTPUT_DIR) / f"url_{index}"
    folder.mkdir(parents=True, exist_ok=True)

    page = browser.new_page()
    resources: List[str] = []

    def handle_request(request: Request) -> None:
        resources.append(request.url)

    page.on("request", handle_request)

    try:
        logger.info(f"Processing URL {index}: {url}")
        page.goto(url, wait_until="networkidle", timeout=WAIT_TIMEOUT_MS)

        html_content = page.content()

        screenshot_path = folder / "screenshot.png"
        page.screenshot(path=str(screenshot_path), full_page=True)

        with open(screenshot_path, "rb") as img_file:
            screenshot_b64 = base64.b64encode(img_file.read()).decode("utf-8")

        data: Dict[str, any] = {
            "html": html_content,
            "resources": resources,
            "screenshot": screenshot_b64,
        }

        output_file = folder / "browse.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Successfully finished processing url_{index}")

    except Exception as e:
        logger.error(f"Error while processing {url}: {e}")

    finally:
        page.close()


def main() -> None:
    urls = load_urls(INPUT_FILE)
    if not urls:
        logger.warning("No URLs found to process. Exiting.")
        return

    logger.info(f"Found {len(urls)} URLs to process.")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for i, url in enumerate(urls, start=1):
            process_url(browser, url, i)

        browser.close()

    logger.info("All done!")


if __name__ == "__main__":
    main()
