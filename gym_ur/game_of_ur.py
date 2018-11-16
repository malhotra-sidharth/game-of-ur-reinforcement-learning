import numpy as np

class GoUrEnv:
  def __init__(self, num_pieces=7):
    """
    Initializes the environment

    num_pieces: number of pawn pices
    """
    #  2D matrix for pieces
    # row 1 for player 1 and row 2 for player 2
    # all set to zero
    self.postions = np.zeros((2, num_pieces), dtype=object)

    # dice roll up
    # 4 pyramidal dice
    self.dice_up = [0, 1, 2, 3, 4]

    # safe position in war zone
    self.safe = [('b', 4)]

    # lands on this column gets a second chance
    self.double_chance = [('a', 1), ('a', 7), ('b', 4), ('c', 1), ('c', 7)]

    # actions_space
    self.action_space_n = num_pieces


    # 4 actions -> forward, left, right, void
    # self.action_space = spaces.Discrete(4)

  def roll(self):
    """
    roll the dice
    :return: random number from dice_up
    """
    return np.random.choice(self.dice_up)


  def is_safe(self, position):
    """
    is safe

    :param position: tuple of position
    :return: boolean: True if safe else false
    """
    return self._search_list_for_tuple(self.safe, position)


  def is_double(self, position):
    """
    if double move

    :param position: tuple of position
    :return: boolean: True if double chance else false
    """
    return self._search_list_for_tuple(self.double_chance, position)


  def get_possible_actions(self, player, dice):
    """
    Returns a list of possible action dictionaries for the given player

    :param player: which player 0 or 1
    :param dice: dice output
    :return:
    """
    actions = []
    movable_piece_ids = {}
    for key, piece in enumerate(self.postions[player]):
      action = self._next_move(piece, player, key, dice)
      # check if no change in positions i.e no possible move
      curr_pos = action['curr_pos']
      next_pos = action['next_pos']
      if curr_pos[0] != next_pos[0] or curr_pos[1] != next_pos[1]:
        actions.append(action)
        movable_piece_ids[action['piece_id'][1]] = action

    return actions, movable_piece_ids


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
    start_row = 'a' if opponent == 0 else 'c'
    self.postions[player][piece_id] = action['next_pos']
    if action['replace_opp']:
      # strike of opponent's piece
      idx = self._find_idx(opponent, action['next_pos'])
      self.postions[opponent][idx] = (start_row, 5)

    if self._is_win(player):
      done = True
      reward = 1

    return (tuple(self.postions[0]), tuple(self.postions[1])), reward, done, {}


  def reset(self):
    self.postions = np.zeros(self.postions.shape, dtype=object)
    return (tuple(self.postions[0]), tuple(self.postions[1]))


  def current_state(self):
    return (tuple(self.postions[0]), tuple(self.postions[1]))


  def _find_idx(self, opponent, next_pos):
    row_next, col_next = next_pos
    for key, (row, col) in enumerate(self.postions[opponent]):
      if row == row_next and col == col_next:
        return key

  def _is_win(self, player):
    """
    Check if the given player has won the game

    :param player:
    :return: boolean, True if given player won else False
    """
    win_row = 'a' if player == 0 else 'c'
    for _, (row, col) in enumerate(self.postions[player]):
      if row != win_row or col != 6:
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
      'replace_opp': None
    }

    if action['curr_pos'] == 0:
      if player == 0:
        self.postions[0][piece_id] = ('a', 5)
        action['curr_pos'] = ('a', 5)
        row, col = ('a', 5)
      else:
        self.postions[1][piece_id] = ('c', 5)
        action['curr_pos'] = ('c', 5)
        row, col = ('c', 5)
    else:
      row, col = action['curr_pos']

    if row == 'a' or row == 'c':
      row, col, replace_opp = self._safe_move(row, col, dice, player)
    else:
      row, col, replace_opp = self._war_move(row, col, dice, player)

    action['replace_opp'] = replace_opp
    action['next_pos'] = (row, col)
    action['double_move'] = self.is_double((row, col))
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
      if self._search_list_for_tuple(self.postions[player2], (row,
                                                                 new_col)):
        if not self.is_safe((row, new_col)):
          replace_opp = True
          col = new_col
        else:
          col = new_col + 1
      else:
        # check if player1 already has any piece at the same position
        if not self._search_list_for_tuple(self.postions[player], (row,
                                                                   new_col)):
          col = new_col
    else:
      # 8 - (col + dice - 8) + 1
      new_col = 17 - col - dice
      new_row = 'a' if player == 0 else 'c'
      if new_col == 6:
        col = 6
        row = new_row
      elif new_col < 6:
        col = col
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
    :return: New postion after making a move in safe zone
    """
    # player 1 is in safe zone
    # check for already existing piece on next position
    # if exists move can't be made
    replace_opp = False
    if col - dice >= 1:
      if col <= 5:
        new_col = col - dice
        # check if there is a piece at new position
        if not self._search_list_for_tuple(self.postions[player], (row,
                                                                   new_col)):
          col = new_col
      elif col - dice == 6:
        col = 6
    else:
      new_col = 1 + np.abs(col - dice)
      new_row = 'b'

      # check if there is a piece at new position
      if not self._search_list_for_tuple(self.postions[player], (new_row,
                                                              new_col)):
        # check for opponent's piece also for replacing
        row, col, replace_opp = self._war_move(new_row, new_col, 0,
                                                     player)

    return row, col, replace_opp

  def _search_list_for_tuple(self, lst, tpl):
    """
    Searches for the given tuple in the given list
    :param lst: list
    :param tpl: tuple to be searched
    :return:
    """
    for ele in lst:
      if isinstance(ele, tuple):
        if ele[0] == tpl[0] and ele[1] == tpl[1]:
          return True

    return False