# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================
from AI import AI
from Action import Action
import copy
from time import time

DEBUG = False
DETAIL_DEBUG = False
TRACK_TIME = True


class MyAI(AI):
    COUNT = 0
    FIRST_START_TIME = 0
    PREV_START_TIME = 0

    def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
        ########################################################################
        #							YOUR CODE BEGINS						   #
        ########################################################################
        self._startX = startX
        self._startY = startY
        self._prevAction = None

        self._uncoverNum = 0
        self._rows = rowDimension
        self._cols = colDimension
        self._totalMines = totalMines
        self._removal_candidates = set()
        self._uncover_candidates = set()
        self._flag_candidates = set()
        self._frontier_dict = dict()
        self._flagNum = 0
        self._startTime = time()
        if MyAI.COUNT == 0:
            MyAI.FIRST_START_TIME = time()
        MyAI.COUNT += 1
        if TRACK_TIME: print(f'world {MyAI.COUNT-1} took', round(self._startTime-MyAI.PREV_START_TIME, 3))
        MyAI.PREV_START_TIME = self._startTime
        # a set of tuples (row, col)
        # contains the position of all tiles whose adjacency hasn't been completely determined
        self._unresolvedTiles: {()} = set()

        # -2: flag, -1: covered, >=0: empty tile/tile with numbers
        row = [-1 for _ in range(colDimension)]
        self._board = [copy.copy(row) for _ in range(rowDimension)]

    ########################################################################
    #							YOUR CODE ENDS							   #
    ########################################################################

    def getAction(self, number: int) -> "Action Object":

        ########################################################################
        #							YOUR CODE BEGINS						   #
        ########################################################################
        if self._uncoverNum == 0:
            self._uncoverNum += 1
            self._prevAction = Action(AI.Action.UNCOVER, self._startX, self._startY)
            return self._prevAction
        elif self._uncoverNum == self._rows * self._cols - self._totalMines:
            if TRACK_TIME: self.printDescription()
            return Action(AI.Action.LEAVE)

        prevX, prevY = self._prevAction.getX(), self._prevAction.getY()
        if number >= 0:
            self._board[prevY][prevX] = number
            self._unresolvedTiles.add((prevX, prevY))

        if DETAIL_DEBUG or DEBUG:
            print()
            self.printBoard()

        for x, y in self._unresolvedTiles:
            if self._numCoveredSurrounding(x, y) == 0:
                self._removal_candidates.add((x, y))
            elif self._board[y][x] == self._numOfAdjacentFlags(x, y):
                self._uncover_candidates = self._uncover_candidates | self._adjacentCoveredTileSet(x, y)
            elif self._numCoveredSurrounding(x, y) == self._board[y][x] - self._numOfAdjacentFlags(x, y):
                self._flag_candidates = self._flag_candidates | self._adjacentCoveredTileSet(x, y)

        if DETAIL_DEBUG: print(len(self._unresolvedTiles), 'unresolved:', self._unresolvedTiles)
        if DETAIL_DEBUG: print(len(self._removal_candidates), 'to remove:', self._removal_candidates)
        for resolvedTile in self._removal_candidates:
            self._unresolvedTiles.remove(resolvedTile)
        self._removal_candidates.clear()

        if len(self._uncover_candidates) == 0 and len(self._flag_candidates) == 0 and len(self._unresolvedTiles) != 0:
            self.model_check()
            if DEBUG or DETAIL_DEBUG:
                print("model check!!!")
        if len(self._uncover_candidates) == 0 and len(self._flag_candidates) == 0 and len(self._unresolvedTiles) == 0:
            # check if all left covered tiles can be uncovered or flagged based on total flags.
            allCoveredTiles = self.getAllCoveredTiles()
            if self._flagNum == self._totalMines:
                self._uncover_candidates = self._uncover_candidates | allCoveredTiles
                print('uncover all is reached')
            elif len(allCoveredTiles) == self._totalMines - self._flagNum:
                self._flag_candidates = self._flag_candidates | allCoveredTiles
                print('flag all is reached')
            # randomly guess if no more clue is available
            elif not self.haveMoreClue(allCoveredTiles):
                x, y = allCoveredTiles.pop()
                self._uncover_candidates.add((x, y))
                print('random guess is reached')

        if DEBUG or DETAIL_DEBUG: print(self._flagNum, 'flags')

        if len(self._uncover_candidates) > 0:
            x, y = self._uncover_candidates.pop()
            action = Action(AI.Action.UNCOVER, x, y)
            if DEBUG or DETAIL_DEBUG: print(f"MyAI: uncover ({x}, {y})")
            self._uncoverNum += 1

        elif len(self._flag_candidates) > 0:
            x, y = self._flag_candidates.pop()
            action = Action(AI.Action.FLAG, x, y)
            if DEBUG or DETAIL_DEBUG: print(f"MyAI: flag ({x}, {y})")
            self._board[y][x] = -2
            self._flagNum += 1
        else:
            print("this should never happen!!!")
            # action = Action(AI.Action.LEAVE)

        self._prevAction = action
        return action

    ########################################################################
    #							YOUR CODE ENDS							   #
    ########################################################################

    # helper function
    # 1 number of covered surrounding
    def _numCoveredSurrounding(self, x, y):
        result = 0
        for c in range(x - 1, x + 2):
            for r in range(y - 1, y + 2):
                if (0 <= c < self._cols and 0 <= r < self._rows) and not (c == x and r == y):
                    if self._board[r][c] == -1:
                        result += 1
        return result

    # 2 number of adjacent flags
    def _numOfAdjacentFlags(self, x, y):
        result = 0
        for c in range(x - 1, x + 2):
            for r in range(y - 1, y + 2):
                if (0 <= c < self._cols and 0 <= r < self._rows) and not (c == x and r == y):
                    if self._board[r][c] == -2:
                        result += 1
        return result

    # 3 set of adjacent covered tile
    def _adjacentCoveredTileSet(self, x, y) -> {()}:
        result = set()
        for c in range(x - 1, x + 2):
            for r in range(y - 1, y + 2):
                if (0 <= c < self._cols and 0 <= r < self._rows) and not (c == x and r == y):
                    if self._board[r][c] == -1:
                        result.add((c, r))
        return result

    def printBoard(self):
        board_as_string = ""
        print('', end=" ")
        for r in range(self._rows - 1, -1, -1):
            print(str(r).ljust(2) + '|', end=" ")
            for c in range(self._cols):
                if self._board[r][c] == -1:
                    print('*', end=" "*len(str(c)))
                elif self._board[r][c] == -2:
                    print('?', end=' '*len(str(c)))
                else:
                    print(self._board[r][c], end=' '*len(str(c)))
            if r != 0:
                print('\n', end=" ")

        col_label = "     "
        col_border = "   "
        for c in range(0, self._cols):
            col_border += "---"
            col_label += str(c) + ' '
        print(board_as_string)
        print(col_border)
        print(col_label)

    # 4 get the frontier based on current unresolved tiles
    def frontier(self) -> dict:
        # the union of covered tiles around each unresolved tile is the frontier
        frontier_dict = dict()
        frontier_set = set()
        for x, y in self._unresolvedTiles:
            frontier_set = frontier_set | self._adjacentCoveredTileSet(x, y)
        for tile in frontier_set:
            frontier_dict[tile] = 0
        return frontier_dict

    # 5 do model check to the frontier and get the possibility
    def model_check(self) -> None:
        # make a frontier dict
        self._frontier_dict = self.frontier()
        # make a list to store frontier
        # store each tile' coordinate with a number that represent their status
        # -1 means 'unassigned', 0 means empty, 1 means mine.
        front_list = [[tile, -1] for tile in self._frontier_dict]

        # variable ordering based on degree heuristics
        front_list.sort(
            key=lambda t: sum(1 if self._board[y][x] > 0 else 0 for x, y in self.getNeighboringTiles(t[0][0], t[0][1])),
            reverse=True)

        self._possibleFrontNum = 0
        self._frontierMineLimit = self._totalMines - self._flagNum
        self.iterCheck(0, front_list)
        # after checking, uncover all the tiles that are impossible to have mines
        # and flag all the tiles that absolutely have mines
        for tile, mineNum in self._frontier_dict.items():
            if mineNum == 0:
                self._uncover_candidates.add(tile)
                if DETAIL_DEBUG: print(tile, 'added to uncover_candidates')
            elif mineNum == self._possibleFrontNum:
                self._flag_candidates.add(tile)
                if DETAIL_DEBUG: print(tile, 'added to flag_candidates')
        # if there is no 100% sure mines or empty tile
        # uncover the tile with the minimum posibility
        if len(self._uncover_candidates) == 0 and len(self._flag_candidates) == 0:
            if DETAIL_DEBUG: print('add', min(self._frontier_dict, key=self._frontier_dict.get),
                                   'to uncover_candidates.')
            self._uncover_candidates.add(min(self._frontier_dict, key=self._frontier_dict.get))

    # 6 set of adjacent signed tile(currently not used)
    def _adjacentSignedTileSet(self, x, y) -> {()}:
        result = set()
        for c in range(x - 1, x + 2):
            for r in range(y - 1, y + 2):
                if (0 <= c < self._cols and 0 <= r < self._rows) and not (c == x and r == y):
                    if self._board[r][c] > 0:
                        result.add((c, r))
        return result

    # 7 assign mine and check validity iteratively
    def iterCheck(self, tile_i: int, front_list: list) -> None:
        # base case: if there is no more frontier tiles to assign
        # check for this case's validity
        # if it's valid, increase the corresponding tile's value in frontier dict
        # then return

        # prune the search branch if the partial assignment cannot lead to a solution.
        if not self.is_solution(front_list, partial=True):
            return
        # if the assignment is complete, check if it is a solution
        elif tile_i == len(front_list):
            if self.is_solution(front_list):
                self._possibleFrontNum += 1
                for tile, tag in front_list:
                    self._frontier_dict[tile] += tag
                return

            else:
                return

        # if it's not the base case, first assign the tile with 1 (is mine)
        # then do this iteratively, until it reach the base case
        frontierMine = sum(1 if tag == 1 else 0 for tile, tag in front_list)
        if frontierMine < self._frontierMineLimit:
            front_list[tile_i][1] = 1
            self.iterCheck(tile_i + 1, front_list)

        # then, when it was returned from the base case, assign the tile with 0 (no mine)
        # and do the check
        front_list[tile_i][1] = 0
        self.iterCheck(tile_i + 1, front_list)

        # if both children have returned, reset the node to unknown and go up one level in the recursion to enter
        # another branch
        front_list[tile_i][1] = -1

    # 8 check the whole frontier's validity
    def is_solution(self, front_list: list, partial=False) -> bool:
        """
        return true if the current assignment is a complete solution when partial = False
        return true if the current assignment is a partial solution when partial = True
        """
        # for every unresolved tile,check if #flag + #assigned mines = #label
        for x, y in self._unresolvedTiles:
            flag_num = self._numOfAdjacentFlags(x, y)
            neighbor = self._adjacentCoveredTileSet(x, y)
            covered_mine = 0
            unassigned_tile = 0
            for tile, tag in front_list:
                if tile in neighbor:
                    if tag == 1:
                        covered_mine += 1
                    elif tag == -1:
                        unassigned_tile += 1
            if partial:
                if covered_mine + flag_num > self._board[y][x]:
                    return False
                elif covered_mine + unassigned_tile + flag_num < self._board[y][x]:
                    # it is theoretically guaranteed not to be a solution, because even if all the covered tiles are
                    # flagged, it cannot satisfy board[y][x]
                    return False
            else:
                if covered_mine + flag_num != self._board[y][x]:
                    return False
        return True

    def printDescription(self):
        finishTime = time()
        t = finishTime - self._startTime
        total = finishTime - MyAI.FIRST_START_TIME
        l = len(str(MyAI.COUNT))
        print(f'world number' + ' ' * (4 - l) + f'{MyAI.COUNT}    ',
              f'time spent: {round(t, 3)}s',
              f'total time: {round(total)}s')

    def getNeighboringTiles(self, x, y) -> set:
        """return a set of tuples corresponding to tiles adjacent to the given coordinate (x, y)"""
        ans = set()
        for c in range(x - 1, x + 2):
            for r in range(y - 1, y + 2):
                if not (c < 0 or c >= self._cols or r < 0 or r >= self._rows) and not (c == x and r == y):
                    ans.add((c, r))
        return ans

    def getAllCoveredTiles(self):
        return {(x, y) for x in range(self._cols) for y in range(self._rows) if self._board[y][x] == -1}

    def haveMoreClue(self, coverdTiles):
        """
        :param coverdTiles the set of tuple coordinates of all covered tiles
        :returns Boolean if there is any covered tile surrounded by uncovered tile
        """
        for x, y in coverdTiles:
            for c in range(x - 1, x + 2):
                for r in range(y - 1, y + 2):
                    if not (c < 0 or c >= self._cols or r < 0 or r >= self._rows) and not (c == x and r == y):
                        if self._board[y][x] >= 0:
                            return True
        return False
