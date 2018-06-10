import numpy as np

class LinearRegressionModel:
    '''
    Linear Regression Model class

    This class implements a machine learning linear regression model. The model is trained
    using stochastic gradient descent to allow online machine learning applications.
    '''

    def __init__(self, dimension, learning_rate, alpha, lambda_const):
        
        self.dimension     = dimension
        self.learning_rate = learning_rate
        self.alpha         = alpha
        self.lambda_const  = lambda_const

        self.coefs_      = np.zeros(self.dimension)
        self.eleg_traces = np.zeros(dimension)


    def reset(self):
        '''
        Resets variables that are dependant on the current game.
        '''

        self.eleg_traces = np.zeros(self.dimension)


    def predict(self, x):
        '''
        Evaluates the current model linear function using the vector 'x' as input.
        '''
        
        x = np.array(x)

        return np.dot(x, self.coefs_)


    def partial_fit(self, X, y):
        '''
        Adjusts the model coefficients using stochastic gradient descent.
        This method expects the data of a fully completed episode.
        '''

        for curr_x, curr_y in zip(X, y):

            pred_score  = self.predict(curr_x)
            delta = curr_y - pred_score
            self.coefs_ = self.coefs_ + ( self.learning_rate * ((delta * curr_x) - (self.alpha * self.coefs_)) )


    def td_lambda(self, prev_state, next_state):
        '''
        Performs one TD(lambda) update step on the model's weights.
        This method should be called after every transition step of the agent being trained.
        '''

        if not prev_state:
            return

        delta = next_state.score - prev_state.score
        self.eleg_traces = (self.lambda_const * self.eleg_traces) + prev_state.features
        self.coefs_ = self.coefs_ + ( delta * self.eleg_traces * self.learning_rate )
