import os
from typing import List
import logging
from mutagen.easyid3 import EasyID3
import pygame

logger = logging.getLogger(__name__)


class MusicPlayer:

    def __init__(self, song_list: List[str], current_index: int, paused: bool, playing: bool) -> None:
        pygame.mixer.init()
        self.song_list: List[str] = song_list
        self.current_index: int = current_index
        self.paused: bool = paused
        self.playing: bool = playing

    def add_songs(self, files: List[str]) -> None:
        self.song_list.extend(files)
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

        pygame.mixer.music.load(self.song_list[self.current_index])
        pygame.mixer.music.play()
        self.playing = True
        self.paused = False
        logger.info("Started to play music")

    def pause(self) -> None:
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

        change_value = 1
        self.change_song(change_value)

    def change_song(self, change_value: int) -> None:
        self.current_index = (self.current_index + change_value) % len(self.song_list)
        logger.info("Playing next song")
        self.play()

    def previous_song(self) -> None:
        if len(self.song_list) == 0:
            return

        change_value = -1
        self.change_song(change_value)

    def handle_song_completion(self) -> None:
        if self.playing and not self.paused and not pygame.mixer.music.get_busy():
            self.next_song()

    def print_song_name(self) -> str:
        if not self.playing:
            return ""

        name = self.get_song_name(self.song_list[self.current_index])
        return "Now playing: " + name
