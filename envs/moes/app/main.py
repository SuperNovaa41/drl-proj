import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) 
sys.path.append(PROJECT_ROOT)

from envs.moes.app import game

# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# How to play: Level select + jump with a
# On opening game, when you die or beat a level, press enter to continue

g = game.game()
# Press the green button in the gutter to run the script.
try:
    if __name__ == '__main__':
        g.gameloop()
except:
    pass

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
