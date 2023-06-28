# TexasPyd'em

This is a little Texas Hold'em game backend, programmed in python (the average pun in in the repository name might have given you a clue).

In the game, you can setup a list of user agents which can be both players and players. The user agents provide an interface the game uses to interact with the agents.

The code only provides the flow and rule control of the game. There are only few, very basic implementations of user agents that allow for playing a game of Texas Hold'em via command line as a single player against simple AI.

Everything else you have to program around. This is what the project is meant for. it serves as a game core.

Especially, you may write your own implementations of the user agents, like spectators with graphical output or much more competent AIs.

## Install

Add the folder _TexasPydDem_ to the modules of your python.

Alternatively, put the folder somewhere and include it in your code using
```
import sys
sys.path.append('./relative/path/to/the/folder')
```

## Play the command line game

The file _TexasPydEm_ is a script that runs a single player game in the console. Change the number and the type of AI players to your needs by editing the file.

## Running the unit tests

Enter ```python3 -m unittest /path/to/UnitTest/HandEvaluator_UT.py``` into the console. Change the name in the end to the name of the file you wanna run the tests for.