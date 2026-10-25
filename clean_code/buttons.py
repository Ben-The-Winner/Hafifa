from abc import ABC, abstractmethod
from typing import Callable, List, Tuple
from tkinter import Button, Frame
from tkinter.filedialog import askopenfilenames
from music_player import MusicPlayer
from settings import Settings


class AbstractButton(ABC):
    def __init__(self, parent_container: Frame, player: MusicPlayer, text: str, row: int,
                 update_callback: Callable[[], None]) -> None:
        self.player = player
        self.update_callback = update_callback
        self.button = Button(
            parent_container,
            text=text,
            width=Settings.BUTTON_WIDTH,
            bg=Settings.BUTTON_BG,
            command=self.handle_button_clicks
        )
        self.button.grid(row=row, column=0)

    def handle_button_clicks(self) -> None:
        self.on_click()
        if self.update_callback:
            self.update_callback()

    @abstractmethod
    def on_click(self) -> None:
        pass


class AddSongButton(AbstractButton):
    def on_click(self) -> None:
        file_types: List[Tuple[str, str]] = [("MP3 files", "*.mp3")]
        files: tuple[str, ...] = askopenfilenames(filetypes=file_types)

        if files:
            self.player.add_songs(list(files))


class PlayButton(AbstractButton):
    def on_click(self) -> None:
        self.player.play()


class PauseUnpauseButton(AbstractButton):
    def on_click(self) -> None:
        self.player.pause()


class PreviousSongButton(AbstractButton):
    def on_click(self) -> None:
        self.player.previous_song()


class NextSongButton(AbstractButton):
    def on_click(self) -> None:
        self.player.next_song()
