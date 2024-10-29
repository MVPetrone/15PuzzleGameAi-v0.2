import time
from tkinter import *
import random


def valueToText(value, max):
    if str(value) == str(max):
        return ""
    else:
        return str(value)


class Game:

    def __init__(self, main):
        self.main = main

        # Properties
        self.fresh = False
        self.old = False
        self.paused = False
        self.w, self.h = self.main.w, self.main.h
        self.x, self.y = 0, 0
        self.moves = 0
        self.timer = 0
        self.timerStart = time.perf_counter()

        # Binds
        self.main.root.bind("<KeyPress>", self.keyPressed)
        #self.main.root.bind("<Return>", self.new)

        self.loadConsoleCommands()

    def load(self, x=20, y=20):
        self.x, self.y = x, y
        # Game
        self.frame = Frame(self.main.root, bd=0)
        self.frame.place(x=self.x, y=self.y)

        # Load Board
        self.board = Board(self, w=4, h=4)
        self.board.load()

        # Load Widgets
        self.widgets = Widgets(self)
        self.widgets.load()

        #self.new()

    def loadConsoleCommands(self):
        # Console
        self.main.console.add_command(name="/get neighbours", command="print(self.app.game.board.getNeighbours())")
        self.main.console.add_command(name="/get solved", command="print(self.app.game.board.getSolved())")
        self.main.console.add_command(name="/reset", command="self.app.game.board.reset()")
        self.main.console.add_command(name="/get boardstate", command="print(self.app.game.board.getBoardState())")

    def keyPressed(self, e=None):
        key = e.keysym
        if key == "Up":
            self.board.move(orient="s")
        elif key == "Right":
            self.board.move(orient="w")
        elif key == "Down":
            self.board.move(orient="n")
        elif key == "Left":
            self.board.move(orient="e")
        elif key == "Return":
            self.new()

    def new(self, e=None):
        self.resetMoves()
        self.resetTimer()
        self.board.scramble()
        self.fresh = True
        self.old = False

    def resetMoves(self):
        self.moves = 0

    def resetTimer(self):
        self.timer = 0
        self.timerStart = time.perf_counter()

    def updateTimer(self):
        # Timer
        if not self.paused:
            if not self.board.complete:
                if not self.fresh:
                    self.timer = time.perf_counter() - self.timerStart

    def update(self):
        # Update Game
        self.board.update()
        self.widgets.update()

        self.updateTimer()


class Widgets:

    def __init__(self, game):
        self.game = game

        # Properties
        self.widgets = []

    def load(self):
        # Widgets frame
        self.frame = Frame(self.game.frame)
        self.frame.grid(column=0, row=1)

        # New
        w, h = 45, 25
        self.newFrame = Frame(self.frame, width=w, height=h, bg="black", bd=2)
        self.newFrame.grid(column=0, row=0)
        self.newCanvas = Canvas(self.newFrame, highlightthickness=0, width=w, height=h, bg="ivory")
        self.newCanvas.create_text(w // 2, h // 2, anchor="center", text="New", font=self.game.main.statTextFont)
        self.newCanvas.bind("<Button-1>", self.new)
        self.newCanvas.pack()

        # Moves
        self.movesLabel = Label(self.frame, text="0 moves", font=self.game.main.statTextFont)
        self.movesLabel.grid(column=1, row=0)

        # Time
        self.timerLabel = Label(self.frame, text="0.00 sec", font=self.game.main.statTextFont)
        self.timerLabel.grid(column=2, row=0)

        # Pause
        self.pauseFrame = Frame(self.frame)
        self.pauseFrame.grid(column=3, row=0)

    def new(self, e=None):
        self.game.new()

    def update(self):
        self.movesLabel.config(text=f"{self.game.moves} moves")
        self.timerLabel.config(text="{:.2f} sec".format(self.game.timer))


class Board:

    def __init__(self, game, w, h):
        self.game = game

        # Properties
        self.complete = True
        self.scrambling = False
        self.w, self.h = w, h

        # Lists
        self.boardState = []
        self.tiles = []

    def load(self):
        # Board
        self.frame = Frame(self.game.frame, bd=4, bg="black")
        self.frame.grid(column=0, row=0, columnspan=3)

        # Load Tiles
        count = 1
        for y in range(self.w):
            for x in range(self.h):
                tile = Tile(self, x=x, y=y, value=count)
                tile.load()
                self.tiles.append(tile)
                count += 1

    def getValues(self):
        values = []
        for tile in self.tiles:
            values.append(tile.value)
        return values

    def getTileFromPos(self, x, y):
        for tile in self.tiles:
            if tile.x == x and tile.y == y:
                return tile

    def getTileFromValue(self, value):
        for tile in self.tiles:
            if tile.value == value:
                return tile

    def getPoses(self):
        poses = []
        for value in range(1, len(self.tiles)+1):
            for tile in self.tiles:
                if tile.value == value:
                    poses.append(tile.getPos())
                    break
        return poses

    def getPosesFromGrid(self):
        # Get poses of grid
        poses = []
        for y in range(self.game.board.h):
            for x in range(self.game.board.w):
                poses.append([x, y])
        return poses

    def getPosesFromValues(self, values):
        gridPoses = self.getPosesFromGrid()
        goalValues = self.getGoalState()

        poses = []
        for value in values:
            for i in range(len(goalValues)):
                if value == goalValues[i]:
                    poses.append(gridPoses[i])
                    break
        return poses

    def getGoalState(self):
        goal = []
        for n in range(1, len(self.tiles) + 1):
            goal.append(n)
        return goal

    def getGoalPoses(self):
        poses = []
        for y in range(self.h):
            for x in range(self.w):
                poses.append([x, y])
        return poses

    def reset(self):
        # Get Goal
        goal = self.getGoalState()

        # Set tiles to goal
        for i in range(len(self.tiles)):
            self.tiles[i].value = goal[i]

    def scramble(self, amount=10000):
        # Reset board to avoid errors
        self.reset()

        # Swap at random, {amount} times
        self.scrambling = True
        for x in range(amount):
            # Gets option and randomises choice
            tile = random.choice(self.tiles)  # Random Tile
            option = random.choice(self.getOptions(tile))  # Choice around empty tile
            self.swap(tile2=option)  # Swap tiles
        self.scrambling = False

    def swap(self, tile1=None, tile2=None):
        """Swaps the value of the two argument tiles
        Filter: uses first ungiven tile to swap empty tile
        """

        # Filters errors
        if tile1 is None:
            tile1 = self.getTileFromValue(len(self.tiles))
        if tile2 is None:
            return

        # Swaps values
        tile1.value, tile2.value = tile2.value, tile1.value

        # Update Counter
        if not self.scrambling:
            if self.game.fresh:
                self.game.resetTimer()
            self.game.fresh = False
            self.game.moves += 1

    def move(self, orient):
        """Move: Uses empty tile position to swap with an adjacent tile with the given orient
        Eg: move(orient="n") = North
            __              __
           |5|             | |
           --     --->     --
          | |             |5|
          --              --   """

        tile = self.getNeighbours(orient=orient)
        self.swap(tile2=tile)

    def getOptions(self, tile):
        """Returns neighbours of argument tile filtered by its options"""

        ops = self.getNeighbours(tile)
        return ops

    def getNeighbours(self, tile=None, orient=None):
        """Returns all available adjacent neighbours in the bounds of the argument tile {type:Tile}"""

        if tile is None:
            tile = self.getTileFromValue(len(self.tiles))  # Default to empty tile

        # Establish neighbours by position
        x, y = tile.x, tile.y
        nesw = [[x, y-1],
                [x+1, y],
                [x, y+1],
                [x-1, y]]

        # Establish tiles by position
        nbs = []
        for n in nesw:
            tile = self.getTileFromPos(x=n[0], y=n[1])
            nbs.append(tile)

        # Filter neighbour returned by orient else return all
        if orient is None:
            while None in nbs: nbs.remove(None)
            return nbs  # All neighbours as Tile objects
        else:
            try:
                if orient == "n":
                    return nbs[0]
                elif orient == "e":
                    return nbs[1]
                elif orient == "s":
                    return nbs[2]
                elif orient == "w":
                    return nbs[3]
                else:
                    raise ValueError("Enter Valid Orientation 'n, e, s, w'")
            except:
                pass

    def getNeighboursFromValues(self, values, orient=None):
        """Returns neighbours {type:pos} from a given set of values"""

        poses = self.getPosesFromGrid()

        # Find empty tile in values and return index
        index = -1
        for i in range(len(values)):
            if values[i] == len(self.tiles):
                index = i
                break
        if index == -1:
            raise ValueError("invalid empty tile in values")


        # Returns neighbours of empty tile in values
        x, y = poses[index][0], poses[index][1]
        nesw = [[x, y - 1],
                [x + 1, y],
                [x, y + 1],
                [x - 1, y]]
        #print("pos:", x, y)
        #print("nei:", nesw)

        # Filter by orient, return positions
        if orient is None:
            # Filter out-of-bounds position
            nbs = []
            for n in nesw:  # n is for neighbour
                count = 0
                for v in n:  # v is for vector
                    if (v >= self.w or v >= self.h) or (v < 0):
                        break
                    else:
                        count += 1
                if count == 2:
                    nbs.append(n)
            return nbs
        #elif orient == "n":


    def checkSolved(self):
        if self.getSolved():
            self.completed()
        else:
            if self.complete:
                self.uncompleted()

    def getSolved(self):
        # Collect values
        values = self.getValues()

        # Generate goal
        goal = self.getGoalState()

        # Check
        if values == goal:
            return True
        else:
            return False

    def completed(self):
        self.old = True
        self.complete = True
        self.config(bg="springgreen2")

    def uncompleted(self):
        self.complete = False
        self.config(bg="ivory")

    def config(self, tiles=None, bg=None):
        if tiles is None:
            tiles = self.tiles

        for tile in tiles:
            tile.config(bg=bg)

    def update(self):
        # Update all tiles
        for tile in self.tiles:
            tile.update()

        # Check if solved
        self.checkSolved()



class Tile:

    def __init__(self, board, value, x, y, pw=64, ph=64, bg="ivory"):
        self.board = board

        # Properties
        self.value = value  # Tile Number
        self.x, self.y = x, y  # Position of Tile
        self.pw, self.ph = pw, ph  # Pixel width, Pixel height
        self.bg = bg

    def load(self):
        root = self.board.frame

        # Frame
        self.frame = Frame(root, width=self.pw, height=self.ph, bg="black", bd=2)
        self.frame.grid(column=self.x, row=self.y)

        # Canvas
        self.canvas = Canvas(self.frame, width=self.pw, height=self.ph, bg=self.bg, highlightthickness=0)
        self.canvas.bind("<Button-1>", self.onPress)
        self.canvas.pack()

        # Text
        self.text = self.canvas.create_text(self.pw//2, self.ph//2, anchor="center", font=self.board.game.main.tileTextFont)

    def onPress(self, e=None):
        """Once clicked on the tile it scans for options around the tile
        if the empty tile is an option it then swaps with it
        else it ignores the click"""

        ops = self.board.getOptions(self)  # Available Options
        emptyTile = self.board.getTileFromValue(len(self.board.tiles))
        if emptyTile in ops:  # Check if empty tile is a neighbour of clicked tile
            self.board.swap(tile2=self)

    def getPos(self):
        pos = [self.x, self.y]
        return pos

    def config(self, bg=None):
        self.canvas.config(bg=bg)

    def update(self):
        self.canvas.itemconfig(self.text, text=valueToText(self.value, len(self.board.tiles)))
