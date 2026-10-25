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
            current_index=0,
            paused=False,
            playing=False
        )

        AddSongButton(self, self.player, "ADD TO LIST", 1, self.refresh_ui)
        PlayButton(self, self.player, "PLAY SONG", 2, self.refresh_ui)
        PauseUnpauseButton(self, self.player, "PAUSE/UNPAUSE", 3, self.refresh_ui)
        PreviousSongButton(self, self.player, "PREVIOUS SONG", 4, self.refresh_ui)
        NextSongButton(self, self.player, "NEXT SONG", 5, self.refresh_ui)

        self.label1 = Label(
            self,
            fg=Settings.LABEL_FG,
            bg=Settings.LABEL_BG,
            font=Settings.LABEL_FONT
        )
        self.label1.grid(row=6, column=0)

        self.text1 = Text(self, wrap=WORD, width=Settings.TEXT_WIDTH)
        self.text1.grid(row=7, column=0)

        self.monitor_playback()

    def refresh_ui(self) -> None:
        self.update_label()
        self.update_list()

    def update_label(self) -> None:
        self.label1['text'] = self.player.print_song_name()

    def update_list(self) -> None:
        self.text1.delete('1.0', END)
        song_number = 1
        for path in self.player.song_list:
            self.text1.insert(END, str(song_number) + ' : ' + self.player.get_song_name(path) + '\n')
            song_number += 1

    def monitor_playback(self) -> None:
        self.player.handle_song_completion()
        self.update_label()
        self.after(Settings.WAIT_TIME_MS, self.monitor_playback)


if __name__ == "__main__":
    window = Tk()
    window.geometry(f"{Settings.WINDOW_WIDTH}x{Settings.WINDOW_HEIGHT}")
    window.title(Settings.WINDOW_TITLE)
    app = FrameApp(window)
    window.mainloop()
