import os
from typing import List
import logging
from mutagen.easyid3 import EasyID3
import pygame

logger = logging.getLogger(__name__)


class MusicPlayer:

    def __init__(self, song_list: List[str], current_song_index: int, paused: bool, playing: bool) -> None:
        pygame.mixer.init()
        self.song_list: List[str] = song_list
        self.current_song_index: int = current_song_index
        self.paused: bool = paused
        self.playing: bool = playing

    def add_songs(self, files: List[str]) -> None:
        self.song_list.extend(files)
        logger.info("Added all the songs.")

    def get_song_name(self, path: str) -> str:
        try:
            song_details = EasyID3(path)
            title = song_details['title'][0]
            artist = song_details['artist'][0]
            return f"{title} - {artist}"
        except Exception:
            return path

    def play(self) -> None:
        if len(self.song_list) == 0:
            return

        pygame.mixer.music.load(self.song_list[self.current_song_index])
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

        next_index = self.player.current_index + 1
        self.player.set_current_song_index(next_index)

    def set_current_song_index(self, index: int) -> None:
        if 0 <= index < len(self.song_list):
            self.current_index = index
            self.play_current_song()

    def previous_song(self) -> None:
        if len(self.song_list) == 0:
            return

        previous_index = self.player.current_index - 1
        self.player.set_current_song_index(previous_index)

    def is_playback_active(self) -> bool:
        return pygame.mixer.music.get_busy()

    def handle_song_completion(self) -> None:
        if self.playing and not self.paused and not is_playback_active():
            self.next_song()

    def get_current_song_name(self) -> str:
        if not self.playing or not self.song_list:
            return ""
        return self.get_song_name(self.song_list[self.current_song_index])
