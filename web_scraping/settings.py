import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    WAIT_TIMEOUT_MS: int = int(os.getenv("WAIT_TIMEOUT_MS", 60000))
    INPUT_FILE: str = os.getenv("INPUT_FILE", "urls.input")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "output")
    SCREENSHOT_FILENAME: str = os.getenv("SCREENSHOT_FILENAME", "screenshot.png")
    OUTPUT_JSON_FILENAME: str = os.getenv("OUTPUT_JSON_FILENAME", "browse.json")
    HEADLESS_MODE: bool = os.getenv("HEADLESS_MODE", "True").lower() in ("true", "1", "yes")