import time
from tkinter import *
from tkinter.font import Font

import random
import maxman

class Ai:

    def __init__(self, game):
        self.game = game

        # Properties
        self.running = False
        self.delay = 0.30  # Seconds
        self.speed = self.delay / 1.00  # Moves per second
        self.x, self.y = 900, 20
        self.w, self.h = 400, 400

        # Lists
        self.paths = []
        self.moveSequence = []  # List of next best moves {type:Value}

        # Console
        self.game.main.console.add_command(name="/get eval", command="print(self.app.game.main.ai.getEval())")

    def load(self, x=900, y=20):
        self.x, self.y = x, y

        # Frame
        self.frame = Frame(self.game.main.root, width=self.w, height=self.h, bd=0)
        self.frame.place(x=self.x, y=self.y)

        # Title label
        self.titleLabel = Label(self.frame, text="AI", font=self.game.main.tileTextFont)
        self.titleLabel.place(x=0, y=0)

        # Eval label
        self.evalLabel = Label(self.frame, text="0 %", font=self.game.main.tileTextFont)
        self.evalLabel.place(x=0, y=50)

        # Next Move Button
        w, h = 150, 40
        #self.nextMoveFrame = Frame(self.frame)
        self.nextMoveButton = Canvas(self.frame, highlightthickness=0, width=w, height=h)
        self.nextMoveButton.place(x=0, y=100)
        self.nextMoveButton.create_rectangle(-1, -1, w, h, fill="grey70")
        self.nextMoveButton.create_text(w//2, h//2, anchor="center", text="Next Move", font=self.game.main.tileTextFont)
        self.nextMoveButton.bind("<Button-1>", self.nextMove)

        self.toggleAIButton = Canvas(self.frame, highlightthickness=0, width=w, height=h)
        self.toggleAIButton.place(x=0, y=150)
        self.toggleAIButton.create_rectangle(-1, -1, w, h, fill="grey70")
        self.toggleAIButton.create_text(w // 2, h // 2, anchor="center", text="Toggle AI",
                                        font=self.game.main.tileTextFont)
        self.toggleAIButton.bind("<Button-1>", self.start)

    def getPosesFromGrid(self):
        # Get poses of grid
        poses = []
        for y in range(self.game.board.h):
            for x in range(self.game.board.w):
                poses.append([x, y])

        return poses

    def getPosesFromValues(self, values):
        # Get poses of grid
        poses = self.getPosesFromGrid()

        # Get poses from values
        poses2 = []
        for i in range(len(values)):  # index of each value
            for p in range(len(poses)):  # pos in default poses
                if values[i] == p + 1:
                    poses2.append(poses[p])
                    break
        return poses2

    def getValuesFromPoses(self, poses):
        poses2 = self.getPosesFromGrid()

        # Get values from poses
        values2 = []
        for p in range(len(poses)):  # index of each value
            for v in range(len(poses2)):  # pos in default poses
                if poses[p] == poses2[v]:
                    values2.append(v + 1)
                    break
        return values2

    def swapPoses(self, values, pos):
        """
        Input values
        Swap values with given position
        Return new values
        """

        # Get poses of grid
        poses = self.getPosesFromGrid()

        # Get poses from values
        poses2 = self.getPosesFromValues(values=values)

        # Get empty tile index
        emptyIndex = -1
        for i in range(len(values)):
            if values[i] == len(self.game.board.tiles):
                emptyIndex = i
                break

        # Get index of pos
        tileIndex = -1
        for i in range(len(poses2)):
            if poses[i] == pos:
                tileIndex = i
                break

        # Swap positions
        poses2[tileIndex], poses2[emptyIndex] = poses2[emptyIndex], poses2[tileIndex]

        # Get values from poses
        values2 = self.getValuesFromPoses(poses=poses2)

        return values2

    def start(self, e=None):
        self.running = not self.running

    def nextMove(self, e=None):
        moveSequence = self.getMoveSequence(layers=5, bestIndex=0)
        moveSequence2 = self.getMoveSequence(layers=5, bestIndex=1)

        # Print
        for x in moveSequence.getPath():
            print(x.getInfo())
        print("")

        for x in moveSequence2.getPath():
            print(x.getInfo())
        print("")

        moveSequenceMean = moveSequence.getEvalsMean()
        moveSequenceMean2 = moveSequence2.getEvalsMean()

        print(moveSequenceMean)
        print(moveSequenceMean2)

        # Move using first option on move sequence
        if moveSequenceMean > moveSequenceMean2:
            option = moveSequence.getPath()[0]
        else:
            option = moveSequence2.getPath()[0]


        # Make Move with option
        if option.pos is not None:
            self.game.board.swap(tile2=self.game.board.getTileFromPos(option.pos[0], option.pos[1]))

    def getMoveSequence(self, layers=1, bestIndex=0, values=None):
        """Use Breadth First Search to evaluate through a series of layers and generate a move sequence that provides
        the best eval outcome {type: Path}"""

        # Define values
        if values is None:
            currentValues = self.game.board.getValues()
        else:
            currentValues = values

        # Gets current evaluation
        currentEval = self.getEval(values=currentValues)

        # Search All layers return all options
        option = Option(layer=0, parentID=-1, ID=0, layerID=0, eval=currentEval, pos=None, state=currentValues)
        moveLayers = {0: [option]}
        idCount = 1
        for l in range(1, layers+1):

            # Get every option in last layer
            moveOptions = []
            layerIDCount = 0
            for o in range(len(moveLayers[l-1])):
                state = moveLayers[l-1][o].state

                # For each move evaluate and store values
                neighbours = self.game.board.getNeighboursFromValues(values=state)  # Neighbours of empty tile in values {type: pos}
                for pos in neighbours:
                    values = self.swapPoses(values=state, pos=pos)
                    eval = self.getEval(values=values)
                    option = Option(layer=l, parentID=o, ID=idCount, layerID=layerIDCount, eval=eval, pos=pos, state=values)
                    moveOptions.append(option)
                    idCount += 1
                    layerIDCount += 1
            moveLayers[l] = moveOptions

        '''print("")
        for l in moveLayers.keys():
            for o in range(len(moveLayers[l])):
                print(moveLayers[l][o].getInfo())
            print("")'''

        # Generate path
        return Path(moveLayers=moveLayers, bestIndex=bestIndex)

    def getEval(self, values=None):
        """
        Get each tile position from board
        Get default tile position of board
        For each tile collect manhatten distance
            abs (start - end) = distance
        Eval (%) = (Sum all distances / total possible distances) * 100
        :return eval:
        """
        # Get max manhatten distance
        max = maxman.getMaxMan(self.game.board.w)

        if values is None:
            # Get current board positions
            poses = self.game.board.getPoses()
        else:
            poses = self.getPosesFromValues(values=values)

        # Get goal board positions
        goals = self.game.board.getGoalPoses()

        # Get total distances of tiles in board
        totalWeight = 0
        for i in range(len(poses)):
            x, y = poses[i][0], poses[i][1]
            #if x != 3 and y != 3:
            x1, y1 = goals[i][0], goals[i][1]
            dist = abs(x-x1) + abs(y-y1)
            totalWeight += dist

        # Calculate % solved of board
        eval = ((max - totalWeight) / max) * 100
        return eval  # Float

    def update(self):
        """Using Mainloop from Main, default tps=100"""
        self.evalLabel.config(text=f"{self.getEval()} %")

        if time.perf_counter() - self.game.main.aiStart > self.delay and self.running:
            self.game.main.aiStart = time.perf_counter()

            self.nextMove()


class Path:
    idCount = 0

    def __init__(self, moveLayers, bestIndex=0):
        self.ID = Path.idCount
        self.moveLayers = moveLayers
        self.option = self.getBestOption(layer=len(moveLayers)-1, index=bestIndex)
        self.path = self.getPath()

        Path.idCount += 1

    def getInfo(self):
        return ["ID: "+str(self.ID), self.path]

    def getPath(self):
        """use option and moveLayers to get the path as indexes {type: Option}"""

        path = [self.option]
        op = self.option
        #print(op.getInfo())
        #print()

        # Go through every option in the layer and make a path of options for option provided
        for layer in range(self.option.layer-1, 0, -1):
            for option in self.moveLayers[layer]:
                if option.layerID == op.parentID:
                    path.append(option)
                    op = option
                    break
        path.reverse()
        self.path = path
        return path

    def getBestOption(self, layer=None, index=0):
        # Get all options from all layers
        if layer is None:
            options = []
            for layer in self.moveLayers:
                for option in self.moveLayers[layer]:
                    options.append(option)
        # Get all options from layer
        else:
            options = self.moveLayers[layer]

        # Get Evals in order
        evals = []
        for option in options:
            evals.append(option.eval)
        sort = evals
        sort = list(dict.fromkeys(sort))  # repeating values are removed
        sort.sort(reverse=True)  # sorts list to highest to lowest
        index = evals.index(sort[index])  # grabs highest value from first position
        self.option = options[index]
        return options[index]

    def getEvals(self):
        # Get all evals
        evals = []
        for option in self.path:
            evals.append(option.eval)
        return evals

    def getEvalsMean(self):
        evals = self.getEvals()

        # Get mean of evals
        total = 0.00
        for eval in evals:
            total += eval
        mean = total/len(evals)

        return mean


class Option:

    def __init__(self, layer, parentID, ID, layerID, eval, pos, state):
        self.layer = layer
        self.parentID = parentID
        self.ID = ID
        self.layerID = layerID
        self.eval = eval
        self.pos = pos
        self.state = state

    def getInfo(self):
        return ["layer: "+ str(self.layer), "parentID: "+str(self.parentID), "ID: "+str(self.ID), "layerID: "+str(self.layerID), "eval: "+str(self.eval), "pos: "+str(self.pos), self.state]
