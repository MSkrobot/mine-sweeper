import pygame
import sys
import random

WIDTH = 30
HEIGHT = 30
N = 10
MARGIN = 3
BOMBS = 10

LEFT_CLICK = 1
RIGHT_CLICK = 3

BLACK = (0, 0, 0)
GRAY = (127, 127, 127)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)


class Stack:
    def __init__(self):
        self.list = []

    def push(self, item):
        self.list.append(item)

    def pop(self):
        return self.list.pop()

    def isEmpty(self):
        return len(self.list) == 0

class Board:
    def __init__(self):
        self.board = [[self.Tile(x, y) for x in range(N)] for y in range(N)]
        self.init = False
        self.game_lost = False
        self.game_won = False
        self.resize = False
    def print(self):
        screen.fill(BLACK)
        for x in range(N):
            for y in range(N):
                tile = self.board[x][y]
                color = WHITE
                if tile.isRevealed:
                    if tile.isBomb:
                        color = RED
                    else:
                        color = GRAY
                elif tile.isFlag:
                    color = BLUE
                pygame.draw.rect(screen, color, [(MARGIN + WIDTH) * y + MARGIN,
                                                 (MARGIN + HEIGHT) * x + MARGIN, WIDTH, HEIGHT])
                tile.printText()
    def endGame(self):
        for x in range(N):
            for y in range(N):
                tile = self.board[x][y]
                if tile.isBomb:
                    tile.isRevealed = True
                tile.isFlag = False

    def generateBombs(self, row, column):
        counter = 0
        while counter < N:
            x = random.randrange(N)
            y = random.randrange(N)
            while x == row:
                x = random.randrange(N)
            while y == column:
                y = random.randrange(N)
            if not self.board[x][y].isBomb:
                counter += 1
                self.board[x][y].isBomb = True

    def newGame(self):
        for x in range(N):
            for y in range(N):
                self.board[x][y].bombNumber = 0
                self.init = False
                self.board[x][y].isRevealed = False
                self.board[x][y].isBomb = False
                self.board[x][y].isVisited = False
                self.board[x][y].isFlag = False
                self.game_lost = False
                self.game_won = False

    def win(self):
        count = 0
        total = N * N
        for x in range(N):
            for y in range(N):
                if self.board[x][y].isRevealed:
                    count += 1
        if ((total - count) == BOMBS) and not self.game_lost:
            self.game_won = True
            for x in range(N):
                for y in range(N):
                    if self.board[x][y].isBomb:
                        self.board[x][y].isFlag = True

    def onClick(self, row, column, button):
        tile = self.board[row][column]
        if self.game_won or self.game_lost:
            self.newGame()
            return
        if not tile.isRevealed:
            if button == LEFT_CLICK and not tile.isFlag:
                if not self.init:
                    self.generateBombs(row, column)
                    self.init = True
                if tile.isBomb:
                    self.endGame()
                    self.game_lost = True
                else:
                    tile.adjacentBombs()
                    if tile.bombNumber == 0:
                        tile.revealAdjacent()
                    tile.isRevealed = True
                self.win()
            elif button == RIGHT_CLICK:
                if not tile.isFlag:
                    tile.isFlag = True
                elif tile.isFlag:
                    tile.isFlag = False

    class Tile:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.isRevealed = False
            self.isBomb = False
            self.isVisited = False
            self.isFlag = False
            self.bombNumber = 0

        def printText(self):
            if self.isRevealed and self.bombNumber != 0:
                digit = font.render(str(self.bombNumber), True, BLACK)
                screen.blit(digit, (self.x * (WIDTH + MARGIN) + 12, self.y * (HEIGHT + MARGIN) + 10))

        def adjacentBombs(self):
            if not self.isVisited:
                self.isVisited = True
                if self.isBomb:
                    return
                for x in range(self.x - 1, self.x + 2):
                    for y in range(self.y - 1, self.y + 2):
                        if (0 <= y < N and 0 <= x < N and (x != self.x or y != self.y)
                                and board.board[y][x].isBomb):
                            self.bombNumber += 1

        def revealAdjacent(self):
            stack = Stack()
            stack.push(self)
            while not stack.isEmpty():
                current = stack.pop()
                column = current.x
                row = current.y
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        if ((x == 0 or y == 0) and x != y
                                and row + x >= 0 and column + y >= 0 and row + x < N and column + y < N):
                            tile = board.board[row + x][column + y]
                            tile.adjacentBombs()
                            if not tile.isRevealed and not tile.isBomb:
                                tile.isRevealed = True
                                tile.isFlag = False
                                if tile.bombNumber == 0:
                                    stack.push(tile)


pygame.init()

size = (N * (WIDTH + MARGIN) + MARGIN, (N * (HEIGHT + MARGIN) + MARGIN))
screen = pygame.display.set_mode(size, pygame.RESIZABLE)
font = pygame.font.Font('freesansbold.ttf', 20)

print(pygame.font.get_fonts())
board = Board()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            column = pos[0] // (WIDTH + MARGIN)
            row = pos[1] // (HEIGHT + MARGIN)
            if row >= N:
                row = N - 1
            if column >= N:
                column = N - 1
            if row >= 0:
                board.onClick(row, column, event.button)
    board.print()
    pygame.display.flip()
