import gym
import numpy as np
from gym import spaces

# dice roll up
# 4 pyramidal dice
dice_up = [0, 1, 2, 3, 4]

# safe position in war zone
safe = [('b', 4)]

# lands on this column gets a second chance
double_chance = [('a', 1), ('a', 7), ('b', 4), ('c', 1), ('c', 7)]

def roll():
  """
  roll the dice
  :return: random number from dice_up
  """
  return np.random.choice(dice_up)

def is_safe(position):
  """
  is safe

  :param position: tuple of position
  :return: boolean: True if safe else false
  """
  return (position in safe)


def is_double(position):
  """
  if double move

  :param position: tuple of position
  :return: boolean: True if double chance else false
  """
  return (position in double_chance)


class GoUrEnv:
  def __init__(self, num_pieces=7):
    #  2D matrix for pieces
    # row 1 for player 1 and row 2 for player 2
    # all set to zero
    self.postions = np.zeros((2, num_pieces))

    # 4 actions -> forward, left, right, void
    # self.action_space = spaces.Discrete(4)


  def get_possible_actions(self, player, dice):
    """
    Returns a list of possible action dictionaries for the given player

    :param player:
    :param dice:
    :return:
    """
    actions = []
    for key, piece in enumerate(self.postions[player]):
      actions.append(self._next_move(piece, player, key, dice))

    return actions


  def step(self, action):
    """
    Takes one step based on the given action

    :param action:
    :return: state, reward, done
    """
    done = False
    reward = 0
    player, piece_id = action['piece_id']
    opponent = 1 if player == 0 else 0
    self.postions[player][piece_id] = action['next_pos']
    if action['replace_opp']:
      # strike of opponent piece
      idx = self.postions[opponent].index(action['next_pos'])
      self.postions[opponent][idx][0] = 'a'
      self.postions[opponent][idx][1] = 5

    if self._is_win(player):
      done = True
      reward = 1

    return self.postions, reward, done, {}

  def reset(self):
    self.postions = np.zeros(self.postions.shape)


  def _is_win(self, player):
    """
    Check if the given player has won the game

    :param player:
    :return: boolean, True if given player won else False
    """
    win_row = 'a' if player == 0 else 'c'
    for row, col in enumerate(self.postions[player]):
      if row != win_row and col != 6:
        return False

      return True


  def _next_move(self, piece, player, piece_id, dice):
    """
    Player 0 starts in row a, col 5 and
    Player 1 starts in row c, col 5

    :param piece:
    :param player:
    :param piece_id:
    :param dice:
    :return: dict, next action based on given parameters and state
    """
    action = {
      'piece_id': (player, piece_id),
      'curr_pos': piece,
      'next_pos': None,
      'double_move': None,
      'replace_opp': False
    }
    row, col = action['curr_pos']
    if row == 'a' or row == 'c':
      row, col = self._next_move(row, col, dice, player)
    else:
      row, col, replace_opp = self._war_move(row, col, dice, player)
      action['replace_opp'] = replace_opp

    action['next_pos'] = (row, col)
    action['double_move'] = is_double((row, col))
    return action


  def _war_move(self, row, col, dice, player):
    """
    Makes a move in warzone

    :param row:
    :param col:
    :param dice:
    :param player:
    :return:
    """
    replace_opp = False
    if col + dice <= 8:
      new_col = col + dice

      # check if there is a piece at new position from
      # other player if yes, strike it off if its not safe
      # if safe place your piece one step ahead of it
      player2 = 0 if player == 1 else 1
      if (row, new_col) in self.postions[player2]:
        if not is_safe((row, new_col)):
          replace_opp = True
          col = new_col
        else:
          col = new_col + 1
      else:
        # check if player1 already has any piece at the same position
        if (row, new_col) not in self.postions[player]:
          col = new_col
    else:
      # 8 - (col + dice - 8) + 1
      new_col = 17 - col - dice
      new_row = 'a' if player == 0 else 'c'
      if new_col <= 6:
        col = 6
      else:
        col = new_col
      row = new_row

    return row, col, replace_opp


  def _safe_move(self, row, col, dice, player):
    """
      Makes a safe move for given player

    :param row:
    :param col:
    :param dice:
    :param player:
    :return:
    """
    # player 1 is in safe zone
    # check for already existing piece on next position
    # if exists move can't be made
    if col - dice >= 1:
      if col <= 5:
        new_col = col - dice
        # check if there is a piece at new position
        if (row, new_col) not in self.postions[player]:
          col = new_col
      elif col - dice == 6:
        col = 6
    else:
      new_col = 1 + np.abs(col - dice)
      new_row = 'b'
      # check if there is a piece at new position
      if (new_row, new_col) not in self.postions[player]:
        col = new_col
        row = new_row

    return row, col