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

class MyAI( AI ):
  COUNT = 0
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

    # a set of tuples (row, col)
    # contains the position of all tiles whose adjacency hasn't been completely determined
    self._unresolvedTiles: {()} = set()

    # -2: flag, -1: covered, >=0: empty tile/tile with numbers
    row = [-1 for _ in range(colDimension)]
    self._board = [ copy.copy(row) for _ in range(rowDimension) ]

  ########################################################################
  #							YOUR CODE ENDS							   #
  ########################################################################



  def getAction(self, number: int) -> "Action Object":

    ########################################################################
    #							YOUR CODE BEGINS						   #
    ########################################################################
    if self._uncoverNum == 0:
      self._startTime = time()
      MyAI.COUNT += 1
      self._uncoverNum += 1
      self._prevAction = Action(AI.Action.UNCOVER, self._startX, self._startY)
      return self._prevAction
    elif self._uncoverNum == self._rows * self._cols - self._totalMines:
      self.printDescription()
      return Action(AI.Action.LEAVE)

    prevX, prevY = self._prevAction.getX(), self._prevAction.getY()
    if number >= 0:
      self._board[prevY][prevX] = number
      self._unresolvedTiles.add( (prevX, prevY) )

    for x, y in self._unresolvedTiles:
      if self._numCoveredSurrounding(x, y) == 0:
        self._removal_candidates.add( (x,y) )
      elif self._board[y][x] == self._numOfAdjacentFlags(x, y):
        self._uncover_candidates = self._uncover_candidates | self._adjacentCoveredTileSet(x, y)
      elif self._numCoveredSurrounding(x, y) == self._board[y][x] - self._numOfAdjacentFlags(x, y):
        self._flag_candidates = self._flag_candidates | self._adjacentCoveredTileSet(x, y)

    for resolvedTile in self._removal_candidates:
      self._unresolvedTiles.remove( resolvedTile )
    self._removal_candidates.clear()

    if len(self._uncover_candidates) == 0 and len(self._flag_candidates) == 0 and len(self._unresolvedTiles) != 0 :
      self.model_check()
      #print("model check!!!")

    if len(self._uncover_candidates) > 0:
      #print(self._uncover_candidates, end ='\n\n')
      #self.printBoard()
      #print()
      x,y = self._uncover_candidates.pop()
      action = Action(AI.Action.UNCOVER, x, y)
      #print(f"MyAI: uncover ({x}, {y})")
      self._uncoverNum += 1

    elif len(self._flag_candidates) > 0:
      x, y = self._flag_candidates.pop()
      action = Action(AI.Action.FLAG, x, y)
      #print(f"MyAI: flag ({x}, {y})")
      self._board[y][x] = -2
      self._flagNum += 1

    else:
      action = Action(AI.Action.LEAVE)
      print('finished')

    self._prevAction = action
    return action

  ########################################################################
  #							YOUR CODE ENDS							   #
  ########################################################################

  #helper function
  #1 number of covered surrounding
  def _numCoveredSurrounding(self, x, y):
    result = 0
    x_range = list(range(x-1, x+2))[(1 if x == 0  else 0):(2 if x == self._rows-1 else 3)]
    y_range = list(range(y-1, y+2))[(1 if y == 0  else 0):(2 if y == self._cols-1 else 3)]
    for i in x_range:
      for j in y_range:
        if i == x and j == y:
          pass
        else:
          if self._board[j][i] == -1:
            result +=1
    return result

  #2 number of adjacent flags
  def _numOfAdjacentFlags(self, x, y):
    result = 0
    x_range = list(range(x-1, x+2))[(1 if x == 0  else 0):(2 if x == self._rows-1 else 3)]
    y_range = list(range(y-1, y+2))[(1 if y == 0  else 0):(2 if y == self._cols-1 else 3)]
    for i in x_range:
      for j in y_range:
        if i == x and j == y:
          pass
        else:
          if self._board[j][i] == -2:
            result +=1
    return result

  #3 set of adjacent covered tile
  def _adjacentCoveredTileSet(self, x, y) -> {()}:
    result = set()
    x_range = list(range(x-1, x+2))[(1 if x == 0  else 0):(2 if x == self._rows-1 else 3)]
    y_range = list(range(y-1, y+2))[(1 if y == 0  else 0):(2 if y == self._cols-1 else 3)]
    for i in x_range:
      for j in y_range:
        if i == x and j == y:
          pass
        else:
          if self._board[j][i] == -1:
            result.add((i, j))
    return result


  def printBoard(self):
    board_as_string = ""
    print('', end = " ")
    for r in range(self._rows-1, -1, -1):
      print(str(r).ljust(2)+'|', end = " ")
      for c in range(self._cols):
        if self._board[r][c] == -1:
          print('*', end = " ")
        elif self._board[r][c] == -2:
          print('f', end = ' ')
        else:
          print(self._board[r][c], end = ' ')
      if(r != 0):
        print('\n', end = " ")

    col_label = "     "
    col_border = "   "
    for c in range(0, self._cols):
      col_border += "---"
      col_label += str(c)+' '
    print(board_as_string)
    print(col_border)
    print(col_label)

  #4 get the frontier based on current unresolved tiles
  def frontier(self) -> dict:
    #the union of covered tiles around each unresolved tile is the frontier
    frontier_dict = dict()
    frontier_set = set()
    for x,y in self._unresolvedTiles:
      frontier_set = frontier_set | self._adjacentCoveredTileSet(x, y)
    for tile in frontier_set:
      frontier_dict[tile] = 0
    return frontier_dict

  #5 do model check to the frontier and get the possibility
  def model_check(self) -> None:
    #make a frontier dict
    self._frontier_dict = self.frontier()
    # make a list to store frontier
    # store each tile' coordinate with a number that represent their status
    # -1 means 'unassigned', 0 means empty, 1 means mine.
    front_list = [[tile, -1] for tile in self._frontier_dict]
    self._possibleFrontNum = 0
    self._frontierMineLimit = self._totalMines - self._flagNum
    self.iterCheck(0, front_list)
    #after checking, uncover all the tiles that are impossible to have mines
    #and flag all the tiles that absolutely have mines
    for tile, mineNum in self._frontier_dict.items():
      if mineNum == 0:
        self._uncover_candidates.add(tile)
      elif mineNum == self._possibleFrontNum:
        self._flag_candidates.add(tile)
    #if there is no 100% sure mines or empty tile
    #uncover the tile with the minimum posibility
    if len(self._uncover_candidates) == 0 and len(self._flag_candidates) == 0:
      self._uncover_candidates.add(min(self._frontier_dict, key = self._frontier_dict.get))

  #6 set of adjacent signed tile(currently not used)
  def _adjacentSignedTileSet(self, x, y) -> {()}:
    result = set()
    x_range = list(range(x-1, x+2))[(1 if x == 0  else 0):(2 if x == self._rows-1 else 3)]
    y_range = list(range(y-1, y+2))[(1 if y == 0  else 0):(2 if y == self._cols-1 else 3)]
    for i in x_range:
      for j in y_range:
        if i == x and j == y:
          pass
        else:
          if self._board[j][i] > 0:
            result.add((i, j))
    return result

  #7 assign mine and check validity iteratively
  def iterCheck(self, tile_i: int, front_list: list) -> None:
    #base case: if there is no more frontier tiles to assign
    #check for this case's validity
    #if it's valid, increase the corresponding tile's value in frontier dict
    #then return
    if(tile_i == len(front_list)):
      if(self.check_frontier_validity(front_list)):
        self._possibleFrontNum += 1
        for i, j in front_list:
          self._frontier_dict[i] += j
      return

    #if it's not the base case, first assign the tile with 0 (no mine)
    #then do this iteratively, until it reach the base case
    front_list[tile_i][1] = 0
    self.iterCheck(tile_i+1, front_list)
    #then, when it was returned from the base case, assign the tile with 1 (with mine)
    #and do the check
    frontierMine = sum([1 if tile[1] == 1 else 0 for tile in front_list ])
    if(frontierMine < self._frontierMineLimit):
      front_list[tile_i][1] = 1
      self.iterCheck(tile_i+1, front_list)
    front_list[tile_i][1] = -1


  #8 check the whole frontier's validity
  def check_frontier_validity(self, front_list: list) -> bool:
    #for every unresolved tile,check if #flag + #assigned mines = #label
    for x,y in self._unresolvedTiles:
      flag_num = self._numOfAdjacentFlags(x,y)
      neighbor = self._adjacentCoveredTileSet(x, y)
      covered_mine = 0
      for i, j in front_list:
        if i in neighbor:
          covered_mine += j
      if covered_mine + flag_num != self._board[y][x]:
        return False
    return True

  def printDescription(self):
    finishTime = time()
    l = len(str(MyAI.COUNT))
    print(f'world number' + ' '*(4-l) + f'{MyAI.COUNT}    ', f'time spent: {round(finishTime-self._startTime, 3)}s')



'''
from AI import AI
from Action import Action
import copy

class MyAI( AI ):

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

    # a set of tuples (row, col)
    # contains the position of all tiles whose adjacency hasn't been completely determined
    self._unresolvedTiles: {()} = set()

    # -2: flag, -1: covered, >=0: empty tile/tile with numbers
    row = [-1 for _ in range(colDimension)]
    self._board = [ copy.copy(row) for _ in range(rowDimension) ]

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
      print("time taken: ")
      return Action(AI.Action.LEAVE)

    prevX, prevY = self._prevAction.getX(), self._prevAction.getY()
    if number >= 0:
      self._board[prevY][prevX] = number
      self._unresolvedTiles.add( (prevX, prevY) )

    for x, y in self._unresolvedTiles:
      if self._numCoveredSurrounding(x, y) == 0:
        self._removal_candidates.add( (x,y) )
      elif self._board[y][x] == self._numOfAdjacentFlags(x, y):
        self._uncover_candidates = self._uncover_candidates | self._adjacentCoveredTileSet(x, y)
      elif self._numCoveredSurrounding(x, y) == self._board[y][x] - self._numOfAdjacentFlags(x, y):
        self._flag_candidates = self._flag_candidates | self._adjacentCoveredTileSet(x, y)

    for resolvedTile in self._removal_candidates:
      self._unresolvedTiles.remove( resolvedTile )
    self._removal_candidates.clear()

    if len(self._uncover_candidates) == 0 and len(self._flag_candidates) == 0 and len(self._unresolvedTiles) != 0 :
      self.model_check()

    if len(self._uncover_candidates) > 0:
      x,y = self._uncover_candidates.pop()
      action = Action(AI.Action.UNCOVER, x, y)
      #self.printBoard()
      #print(self._uncover_candidates, end ='\n\n')
      #print(f"MyAI: uncover ({x}, {y})")
      self._uncoverNum += 1

    elif len(self._flag_candidates) > 0:
      x, y = self._flag_candidates.pop()
      action = Action(AI.Action.FLAG, x, y)
      # print(f"MyAI: flag ({x}, {y})")
      self._board[y][x] = -2

    else:
      action = Action(AI.Action.LEAVE)

    self._prevAction = action
    return action

  ########################################################################
  #							YOUR CODE ENDS							   #
  ########################################################################

  #helper function
  #1 number of covered surrounding
  def _numCoveredSurrounding(self, x, y):
    result = 0
    x_range = list(range(x-1, x+2))[(1 if x == 0  else 0):(2 if x == self._rows-1 else 3)]
    y_range = list(range(y-1, y+2))[(1 if y == 0  else 0):(2 if y == self._cols-1 else 3)]
    for i in x_range:
      for j in y_range:
        if i == x and j == y:
          pass
        else:
          if self._board[j][i] == -1:
            result +=1
    return result

  #2 number of adjacent flags
  def _numOfAdjacentFlags(self, x, y):
    result = 0
    x_range = list(range(x-1, x+2))[(1 if x == 0  else 0):(2 if x == self._rows-1 else 3)]
    y_range = list(range(y-1, y+2))[(1 if y == 0  else 0):(2 if y == self._cols-1 else 3)]
    for i in x_range:
      for j in y_range:
        if i == x and j == y:
          pass
        else:
          if self._board[j][i] == -2:
            result +=1
    return result

  #3 set of adjacent covered tile
  def _adjacentCoveredTileSet(self, x, y) -> {()}:
    result = set()
    x_range = list(range(x-1, x+2))[(1 if x == 0  else 0):(2 if x == self._rows-1 else 3)]
    y_range = list(range(y-1, y+2))[(1 if y == 0  else 0):(2 if y == self._cols-1 else 3)]
    for i in x_range:
      for j in y_range:
        if i == x and j == y:
          pass
        else:
          if self._board[j][i] == -1:
            result.add((i, j))
    return result


  def printBoard(self):
    board_as_string = ""
    print('', end = " ")
    for r in range(self._rows-1, -1, -1):
      print(str(r).ljust(2)+'|', end = " ")
      for c in range(self._cols):
        if self._board[r][c] == -1:
          print('*', end = " ")
        elif self._board[r][c] == -2:
          print('f', end = ' ')
        else:
          print(self._board[r][c], end = ' ')
      if(r != 0):
        print('\n', end = " ")

    col_label = "     "
    col_border = "   "
    for c in range(0, self._cols):
      col_border += "---"
      col_label += str(c)+' '
    print(board_as_string)
    print(col_border)
    print(col_label)

  #4 get the frontier based on current unresolved tiles
  def frontier(self) -> dict:
    #the union of covered tiles around each unresolved tile is the frontier
    frontier_dict = dict()
    frontier_set = set()
    for x,y in self._unresolvedTiles:
      frontier_set = frontier_set | self._adjacentCoveredTileSet(x, y)
    for tile in frontier_set:
      frontier_dict[tile] = 0
    return frontier_dict

  #5 do model check to the frontier and get the possibility
  def model_check(self) -> None:
    #make a frontier dict
    self._frontier_dict = self.frontier()
    # make a list to store frontier
    # store each tile' coordinate with a number that represent their status
    # -1 means 'unassigned', 0 means empty, 1 means mine.
    front_list = [[tile, -1] for tile in self._frontier_dict]
    self._possibleFrontNum = 0
    self.iterCheck(0, front_list)
    #after checking, uncover all the tiles that are impossible to have mines
    #and flag all the tiles that absolutely have mines
    for tile, mineNum in self._frontier_dict.items():
      if mineNum == 0:
        self._uncover_candidates.add(tile)
      elif mineNum == self._possibleFrontNum:
        self._flag_candidates.add(tile)
    #if there is no 100% sure mines or empty tile
    #uncover the tile with the minimum posibility
    if len(self._uncover_candidates) == 0 and len(self._flag_candidates) == 0:
      self._uncover_candidates.add(min(self._frontier_dict, key = self._frontier_dict.get))

  #6 set of adjacent signed tile(currently not used)
  def _adjacentSignedTileSet(self, x, y) -> {()}:
    result = set()
    x_range = list(range(x-1, x+2))[(1 if x == 0  else 0):(2 if x == self._rows-1 else 3)]
    y_range = list(range(y-1, y+2))[(1 if y == 0  else 0):(2 if y == self._cols-1 else 3)]
    for i in x_range:
      for j in y_range:
        if i == x and j == y:
          pass
        else:
          if self._board[j][i] > 0:
            result.add((i, j))
    return result

  #7 assign mine and check validity iteratively
  def iterCheck(self, tile_i: int, front_list: list) -> None:
    #base case: if there is no more frontier tiles to assign
    #check for this case's validity
    #if it's valid, increase the corresponding tile's value in frontier dict
    #then return
    if(tile_i == len(front_list)):
      if(self.check_frontier_validity(front_list)):
        for i, j in front_list:
          self._frontier_dict[i] += j
          self._possibleFrontNum += 1
      return

    #if it's not the base case, first assign the tile with 0 (no mine)
    #then do this iteratively, until it reach the base case
    front_list[tile_i][1] = 0
    self.iterCheck(tile_i+1, front_list)
    #then, when it was returned from the base case, assign the tile with 1 (with mine)
    #and do the check
    front_list[tile_i][1] = 1
    self.iterCheck(tile_i+1, front_list)

  #8 check the whole frontier's validity
  def check_frontier_validity(self, front_list: list) -> bool:
    #for every unresolved tile,check if #flag + #assigned mines = #label
    for x,y in self._unresolvedTiles:
      flag_num = self._numOfAdjacentFlags(x,y)
      neighbor = self._adjacentCoveredTileSet(x, y)
      covered_mine = 0
      for i, j in front_list:
        if i in neighbor:
          covered_mine += j
      if covered_mine + flag_num != self._board[y][x]:
        return False
    return True
'''