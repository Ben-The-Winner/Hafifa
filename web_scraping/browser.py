import base64
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from playwright.sync_api import Request, Browser, Page, sync_playwright
from settings import Settings


logger = logging.getLogger(__name__)


class RequestHandler:

    def __init__(self, requested_urls: List[str]) -> None:
        self.requested_urls = requested_urls

    def handle_request(self, request: Request) -> None:
        self.requested_urls.append(request.url)


def load_urls(file_path: str) -> List[str]:
    path = Path(file_path)

    with open(path, "r", encoding="utf-8") as file:
        return [
            line.strip()
            for line in file
            if line.strip()
        ]


def create_output_folder(index: int) -> Path:
    folder = Path(Settings.OUTPUT_DIR) / f"url_{index}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def capture_screenshot(page: Page, folder: Path) -> str:
    screenshot_path = folder / Settings.SCREENSHOT_FILENAME

    page.screenshot(
        path=str(screenshot_path),
        full_page=True,
    )

    with open(screenshot_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def save_results(folder: Path, content: Dict[str, Any]) -> None:
    output_file = folder / Settings.OUTPUT_JSON_FILENAME

    print("Saving to:", output_file.resolve())

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            content,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print("Saved at:", output_file.stat().st_mtime)


def process_url(browser: Browser, url: str, index: int) -> None:
    folder = create_output_folder(index)
    page = browser.new_page()
    requested_urls: List[str] = []

    request_handler = RequestHandler(requested_urls)
    page.on("request", request_handler.handle_request)

    try:
        logger.info(f"Processing URL {index}: {url}")

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=Settings.WAIT_TIMEOUT_MS,
        )

        html_content = page.content()
        screenshot_b64 = capture_screenshot(page, folder)

        resources: Dict[str, Any] = {
            "html": html_content,
            "requested_urls": requested_urls,
            "screenshot": screenshot_b64,
        }

        save_results(folder, resources)
        logger.info(f"Successfully finished processing url_{index}")

    except Exception:
        logger.exception(f"Error while processing {url}")

    finally:
        page.close()


def main() -> None:
    print("Output directory:", Path(Settings.OUTPUT_DIR).resolve())
    urls = load_urls(Settings.INPUT_FILE)

    if not urls:
        logger.warning("No URLs found to process. Exiting.")
        return

    logger.info(f"Found {len(urls)} URLs to process.")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)

        try:
            for index, url in enumerate(urls, start=1):
                process_url(browser, url, index)
        finally:
            browser.close()

    logger.info("All done!")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    main()
