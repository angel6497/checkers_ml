# **checkers_ml**

<br />

## Description

**checkers_ml** is a Python implementation of checkers that uses reinforcement learning for the purpose
of providing a computer opponent against which a user can play.

The agent uses a combination of a linear function approximation with 38 features and the minimax algorithm to make decisions during the game. The linear function is trained using the TDLeaf Lambda variation of the temporal difference algorithm.


## Getting Started

The project requires Python 3, more specifically Python 3.4 or higher. The following instructions will assume that the appropiate Python version is already installed.


### Pipenv and Depencencies

The easiest way to install the project is to use Pipenv. If you don't have it installed, you can get it with pip:

```shell
$ pip3 install pipenv
```

Once Pipenv is installed, you can clone the repository and install the dependencies.

```shell
$ git clone https://github.com/angel6497/checkers_ml
$ cd checkers_ml
$ pipenv install --three
```

After doing this Pipenv will create a virtual environment with all the dependencies of the project. If you have multiple versions of Python 3 installed on your system, you can pick a specific one when creating the environment by replacing the option `--three` with `--python 3.4` or whichever version you want to use. To activate the environment use:

```shell
$ pipenv shell
```

You can exit the virtual environment using CTRL-D.


### GUI

If you want yo use the Checkers GUI, you must install it by running:

```shell
$ make
```


## Training an Agent

You can have an agent train by playing itself N times. If N is zero, it will keep training until it is stopped with CTRL-C.

```shell
$ ./start.py -train N
```

The hyperparameters of the training algorithm can be changed in controller.py in the checkersml package.


## Playing Checkers

To play a match against the the agent or another human player use the `-play` option.

```shell
$ ./start.py -play N
```

The argument N is the number of real players in the match. 

* N = 0 displays a match between two RL agents, so the program will never give control to the user.
* N = 1 has the user play against the trained RL agent.
* N = 2 allows two human players to play against each other.


## License

This project is licensed under the MIT License - see the LICENSE file for details
