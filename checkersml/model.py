import numpy as np

class LinearRegressionModel:
    '''
    LinearRegressionModel class

    This class implements a machine learning linear regression model. The model is trained
    using stochastic gradient descent to allow online machine learning applications.
    '''

    def __init__(self, dimension, learning_rate, alpha):
        
        self.dimension     = dimension
        self.learning_rate = learning_rate
        self.alpha         = alpha

        self.coefs_ = np.zeros(self.dimension + 1)


    def predict(self, x):
        '''
        Evaluates the current model linear function using the vector 'x' as input.
        '''
        
        x = np.array(x)
        x = np.insert(x, 0, 1) 

        return np.dot(x, self.coefs_)


    def partial_fit(self, X, y):
        '''
        Adjusts the model coefficient using stochastic gradient descent.
        '''

        for curr_x, curr_y in zip(X, y):

            pred_score  = self.predict(curr_x)
            curr_x      = np.insert(curr_x, 0, 1)
            
            self.coefs_ = ( self.coefs_ + ( self.learning_rate * ( ((curr_y - pred_score) * curr_x) 
                                                                 - (self.alpha * self.coefs_) ) ) )

