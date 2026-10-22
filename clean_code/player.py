from abc import ABC, abstractmethod
import os
from typing import List, Callable
import logging

from mutagen.easyid3 import EasyID3
import pygame
from tkinter import *
from tkinter.filedialog import askopenfilenames

wait_some_time = 500

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


#################################################################################
class MusicPlayer:

    def __init__(self) -> None:
        pygame.mixer.init()
        self.song_list: List[str] = []
        self.list_index: int = 0
        self.paused: bool = False
        self.playing: bool = False

    def add_songs(self, files: List[str]) -> None:
        for new_song in files:
            self.song_list.append(new_song)
        logger.info("Added all the songs.")

    def get_song_name(self, path: str) -> str:
        try:
            tags = EasyID3(path)
            return tags['title'][0] + ' - ' + tags['artist'][0]
        except Exception:
            return os.path.basename(path)

    def play(self) -> None:
        if len(self.song_list) == 0:
            return

        pygame.mixer.music.load(self.song_list[self.list_index])
        pygame.mixer.music.play()
        self.playing = True
        self.paused = False
        logger.info("Started to play music")

    def pause_unpause(self) -> None:
        if not self.playing:
            return

        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            logger.info("Music unpaused")
        else:
            pygame.mixer.music.pause()
            self.paused = True
            logger.info("Music paused")

    def next_song(self) -> None:
        if len(self.song_list) == 0:
            return

        next_val = 1
        self.change_song(next_val)

    def change_song(self, next_previous: int) -> None:
        self.list_index = (self.list_index + next_previous) % len(self.song_list)
        logger.info("Playing next song")
        self.play()

    def previous_song(self) -> None:
        if len(self.song_list) == 0:
            return

        previous_val = -1
        self.change_song(previous_val)

    def check_song_end(self) -> None:
        if self.playing and not self.paused and not pygame.mixer.music.get_busy():
            self.next_song()

    def now_playing_text(self) -> str:
        if not self.playing:
            return ""

        name = self.get_song_name(self.song_list[self.list_index])
        return "Now playing: " + name


#################################################################################
class AbstractButton(ABC):
    def __init__(self, parent_container: Frame, player: MusicPlayer, text: str, row: int, update_callback: Callable[[], None]) -> None:
        self.player = player
        self.update_callback = update_callback
        self.button = Button(parent_container, text=text, width=40, bg='AntiqueWhite1', command=self.click)
        self.button.grid(row=row, column=0)

    def click(self) -> None:
        self.on_click()
        if self.update_callback:
            self.update_callback()

    @abstractmethod
    def on_click(self) -> None:
        pass


class AddSongButton(AbstractButton):
    def on_click(self) -> None:
        files = askopenfilenames(filetypes=[("MP3 files", "*.mp3")])
        if files:
            self.player.add_songs(files)


class PlayButton(AbstractButton):
    def on_click(self) -> None:
        self.player.play()


class PauseUnpauseButton(AbstractButton):
    def on_click(self) -> None:
        self.player.pause_unpause()


class PreviousSongButton(AbstractButton):
    def on_click(self) -> None:
        self.player.previous_song()


class NextSongButton(AbstractButton):
    def on_click(self) -> None:
        self.player.next_song()


#################################################################################
class FrameApp(Frame):

    def __init__(self, master: Tk) -> None:
        super().__init__(master)
        self.grid()
        self.player = MusicPlayer()

        AddSongButton(self, self.player, "ADD TO LIST", 1, self.refresh_ui)
        PlayButton(self, self.player, "PLAY SONG", 2, self.refresh_ui)
        PauseUnpauseButton(self, self.player, "PAUSE/UNPAUSE", 3, self.refresh_ui)
        PreviousSongButton(self, self.player, "PREVIOUS SONG", 4, self.refresh_ui)
        NextSongButton(self, self.player, "NEXT SONG", 5, self.refresh_ui)

        self.label1 = Label(self, fg='Black', bg='ivory2',
                            font=('Helvetica', 10, 'bold italic'))
        self.label1.grid(row=6, column=0)

        self.text1 = Text(self, wrap=WORD, width=60)
        self.text1.grid(row=7, column=0)

        self.check_music()

    def refresh_ui(self) -> None:
        self.update_label()
        self.update_list()

    def update_label(self) -> None:
        self.label1['text'] = self.player.now_playing_text()

    def update_list(self) -> None:
        self.text1.delete('1.0', END)
        song_number = 1
        for path in self.player.song_list:
            self.text1.insert(END, str(song_number) + ' : ' + self.player.get_song_name(path) + '\n')
            song_number += 1

    def check_music(self) -> None:
        self.player.check_song_end()
        self.update_label()
        self.after(wait_some_time, self.check_music)
#################################################################################


window = Tk()
window.geometry("500x500")
window.title("MP3 Music Player")
app = FrameApp(window)
window.mainloop()
