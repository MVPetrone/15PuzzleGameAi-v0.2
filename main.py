import time
from tkinter import *
from tkinter.font import Font
import console
import game
import ai


class Main:

    def __init__(self, width=1400, height=600):
        self.running = True
        self.root = Tk()

        # Properties
        self.fps = 0
        self.title = "15 Puzzle Game v0.2"
        self.w, self.h = width, height

        # Window
        self.root.title(self.title)
        self.root.geometry(f"{self.w}x{self.h}")
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        # Font
        self.tileTextFont = Font(family="times", size=20, weight="bold")
        self.statTextFont = Font(family="times", size=14, weight="bold")

        # Load
        self.load()

    def load(self):
        # Console
        self.console = console.Console(app=self)

        # Game 1
        self.game = game.Game(self)
        self.game.load(x=500, y=20)

        # Ai
        self.ai = ai.Ai(game=self.game)
        self.ai.load(x=900, y=20)

    def mainloop(self, fps=100):
        self.fps = fps

        # Mainloop
        self.start = time.perf_counter()
        self.aiStart = time.perf_counter()
        while self.running:
            if time.perf_counter() - self.start > (1/self.fps):
                self.start = time.perf_counter()

                # Update
                self.update()

    def quit(self):
        self.running = False

    def update(self):
        self.game.update()
        self.ai.update()
        self.root.update()


if __name__ == '__main__':
    main = Main()
    main.mainloop(fps=100)