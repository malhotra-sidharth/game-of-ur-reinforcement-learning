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

# roll the dice
def roll():
  return np.random.choice(dice_up)


# is safe
def is_safe(state):
  """
  :param state: tuple of position
  :return: boolean: True if safe else false
  """
  return (state in safe)


# if double move
def is_double(state):
  """
  :param state: tuple of position
  :return: boolean: True if double chance else false
  """
  return (state in double_chance)


class GoUrEnv:
  def __init__(self):

