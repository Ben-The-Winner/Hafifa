import logging
from tkinter import *
from settings import Settings
from music_player import MusicPlayer
from buttons import (
    AddSongButton,
    PlayButton,
    PauseUnpauseButton,
    PreviousSongButton,
    NextSongButton
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class FrameApp(Frame):

    def __init__(self, master: Tk) -> None:
        super().__init__(master)
        self.grid()

        self.player = MusicPlayer(
            song_list=[],
            current_song_index=0,
            paused=False,
            playing=False
        )

        AddSongButton(self, self.player, "ADD TO LIST", 1, self.refresh_ui)
        PlayButton(self, self.player, "PLAY SONG", 2, self.refresh_ui)
        PauseUnpauseButton(self, self.player, "PAUSE/UNPAUSE", 3, self.refresh_ui)
        PreviousSongButton(self, self.player, "PREVIOUS SONG", 4, self.refresh_ui)
        NextSongButton(self, self.player, "NEXT SONG", 5, self.refresh_ui)

        self.song_display_label = Label(
            self,
            fg=Settings.LABEL_FG,
            bg=Settings.LABEL_BG,
            font=Settings.LABEL_FONT
        )
        self.song_display_label.grid(row=6, column=0)

        self.playlist_display = Text(self, wrap=WORD, width=Settings.TEXT_WIDTH)
        self.playlist_display.grid(row=7, column=0)

        self.monitor_playback()

    def refresh_ui(self) -> None:
        self.refresh_current_song_display()
        self.refresh_playlist_view()

    def refresh_current_song_display(self) -> None:
        current_song = self.player.get_current_song_name()
        display_text = f"Now playing: {current_song}" if current_song else ""
        self.song_display_label['text'] = display_text

    def refresh_playlist_view(self) -> None:
        self.clear_playlist_display()
        self.populate_playlist_display()

    def clear_playlist_display(self) -> None:
        self.playlist_display.delete('1.0', END)

    def populate_playlist_display(self) -> None:
        for song_number, path in enumerate(self.player.song_list, start=1):
            song_name = self.player.get_song_name(path)
            self.playlist_display.insert(END, f"{song_number} : {song_name}\n")

    def monitor_playback(self) -> None:
        self.player.handle_song_completion()
        self.refresh_current_song_display()
        self.after(Settings.WAIT_TIME_MS, self.monitor_playback)


if __name__ == "__main__":
    window = Tk()
    window.geometry(f"{Settings.WINDOW_WIDTH}x{Settings.WINDOW_HEIGHT}")
    window.title(Settings.WINDOW_TITLE)
    app = FrameApp(window)
    window.mainloop()
