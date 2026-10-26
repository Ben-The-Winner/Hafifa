import os
from typing import List
import logging
from mutagen.easyid3 import EasyID3
import pygame
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)


class MusicPlayer:

    def __init__(self, song_list: List[str], current_song_index: int, paused: bool, playing: bool) -> None:
        pygame.mixer.init()
        self.song_list: List[str] = song_list
        self.current_song_index: int = current_song_index
        self.paused: bool = paused
        self.playing: bool = playing

    def ensure_playlist_not_empty(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            if not self.song_list:
                return
            return func(self, *args, **kwargs)

        return wrapper

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

    @ensure_playlist_not_empty
    def play(self) -> None:
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

    @ensure_playlist_not_empty
    def next_song(self) -> None:
        next_index = self.current_song_index + 1
        self.set_current_song_index(next_index)

    def set_current_song_index(self, index: int) -> None:
        if 0 <= index < len(self.song_list):
            self.current_song_index = index
            self.play()

    @ensure_playlist_not_empty
    def previous_song(self) -> None:
        previous_index = self.current_song_index - 1
        self.set_current_song_index(previous_index)

    def is_playback_active(self) -> bool:
        return pygame.mixer.music.get_busy()

    def handle_song_completion(self) -> None:
        if self.playing and not self.paused and not self.is_playback_active():
            self.next_song()

    @ensure_playlist_not_empty
    def get_current_song_name(self) -> str:
        if not self.playing:
            return ""
        return self.get_song_name(self.song_list[self.current_song_index])
