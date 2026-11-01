import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    WAIT_TIMEOUT_MS: int = int(os.environ["WAIT_TIMEOUT_MS"])
    INPUT_FILE: str = os.environ["INPUT_FILE"]
    OUTPUT_DIR: str = os.environ["OUTPUT_DIR"]
    SCREENSHOT_FILENAME: str = os.environ["SCREENSHOT_FILENAME"]
    OUTPUT_JSON_FILENAME: str = os.environ["OUTPUT_JSON_FILENAME"]
    HEADLESS_MODE: bool = os.environ["HEADLESS_MODE"].lower() in ("true", "1", "yes")
