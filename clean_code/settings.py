import os
from typing import List, Tuple
from dotenv import load_dotenv

load_dotenv()


class Settings:
    WINDOW_WIDTH = int(os.environ["WINDOW_WIDTH"])
    WINDOW_HEIGHT = int(os.environ["WINDOW_HEIGHT"])
    WINDOW_TITLE = os.environ["WINDOW_TITLE"]
    WAIT_TIME_MS = int(os.environ["WAIT_TIME_MS"])

    BUTTON_WIDTH = int(os.environ["BUTTON_WIDTH"])
    BUTTON_BG = os.environ["BUTTON_BG"]
    LABEL_FG = os.environ["LABEL_FG"]
    LABEL_BG = os.environ["LABEL_BG"]
    LABEL_FONT = (os.environ["LABEL_FONT_NAME"], int(os.environ["LABEL_FONT_SIZE"]), os.environ["LABEL_FONT_STYLE"])
    TEXT_WIDTH = int(os.environ["TEXT_WIDTH"])

    AUDIO_FILE_TYPES: List[Tuple[str, str]] = [("MP3 files", "*.mp3")]
