# **checkers_ml**

<br />

## Description

**checkers_ml** is a Python implementation of checkers that uses machine learning for the purpose
of providing a computer opponent against which a user can play.

## Status

Application is currently working. 

At this point the application provides regular play functionality either against a computer or another real player, and trainning functionality which trains a simple linear regression model by having it play against itself. The model represents the entire board states through 6 features, and the learning algorithm used is stochastic gradient descent. Right now the model can achieve 70% win rate against a random untrained player.

Currently working on a machine learning player with a higher performance. To achieve this, the current hypothesis, a linear function will be replaced with a neural network. Additionally, the simplification that maps the board state to 6 features will be removed effectively having 32 features instead.
