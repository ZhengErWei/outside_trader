#documentation: https://github.com/JWarmenhoven/ISLR-python/blob/master/Notebooks/Chapter%206.ipynb
import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.model_selection import KFold, cross_val_score
from sklearn.metrics import mean_squared_error, classification_report,\
                            confusion_matrix
from sklearn.cross_decomposition import PLSRegression
from sklearn.linear_model import LogisticRegression
from pylab import rcParams
from sklearn.preprocessing import scale 

#PCR
class PCR_mod:

    def __init__(self, k, x_train, y_train, x_test, y_test, test_in):
        '''
        Construct a principal component logistic regression model on the 
        data passed. 

        Input:
          k: integer, >=2, parameter for cross validation to calculate 
             mean square error for each principal component
          x_train: dataframe, training set for predictors
          y_train: series, training set for dependet variable
          x_test: dataframe, testing set for predictors
          y_test: series, testing set for dependent variable
          test_in: series, price percentage increase in testing set

        Return:
          mse: list, the list of mean square error for each principal 
               component
          best_n: the number of component with least mean square error
          min_error: the minimum mean square error
          y_pred: series, best prediction made based on all given attributes
          confusion_matrix: numpy array, the confusion matrix for y_pred and 
                            y_test
          report: string, the classification report 
          prot_shape: integer, the size of portfolio predicted from testing 
                      set
          exp_rv: float, the expected percentage increase from the portfolio
        '''

        self.k_fold = k
        self.x_train = x_train
        self.y_train = y_train
        self.x_test = x_test
        self.y_test = y_test
        self.test_in = test_in
        self.mse, self.best_n, self.min_error = self.find_best_pca(x_train, \
                                                                   y_train)
        self.graph = self.draw_pca_graph(self.mse)
        self.y_pred = self.get_prediction(self.best_n, x_train, y_train, 
        	                              x_test)
        self.confusion_matrix = self.get_confusion_matrix(self.y_test, \
                              self.y_pred)
        self.report = self.get_precision_table(self.y_test, self.y_pred)
        self.port_shape, self.exp_rv = \
                    self.get_portfolio_detail(self.test_in, self.y_pred)


    #'MODIFIED'
    def find_best_pca(self, x_train, y_train):
        '''
        Get the number of componet which give minumum mean square error
        from the data for x and y

        Input:
          x_trian: x_train: dataframe, the data for x training set
          y_train: series, the data for y training set

        Return: list, integer
        '''
        pca = PCA()
        x_reduced_train = pca.fit_transform(scale(x_train))
        n = len(x_reduced_train)
        kf = KFold(n_splits= self.k_fold, shuffle=False, random_state=1)
        mse = []
        log = LogisticRegression(solver='newton-cg')    
        score = -1 * cross_val_score(log, np.ones((n,1)), y_train, cv=kf, \
                                     scoring='neg_mean_squared_error').mean()    
        mse.append(score) 
        for i in np.arange(1, x_train.shape[1] + 1):
            score = abs(cross_val_score(log, x_reduced_train[:,:i], y_train, \
                        cv=kf, scoring='neg_mean_squared_error')).mean()
            mse.append(score)
        min_error = min(mse)
    
        return mse, mse.index(min_error), min_error  
    
    #"MODIFIED"
    def get_prediction(self, num, x_train, y_train, x_test):
        '''
        Get the prediction based from the training set and testing set

        Input:
          num: integer, number of principal components
          x_train: dataframe, the data for x training set
          y_train: series, the data for x training set
          x_test: dataframe, the data for x testing set

        Return: series
        '''
        pca = PCA()
        x_reduced_train = pca.fit_transform(scale(x_train))
        x_reduced_test = pca.transform(scale(x_test))[:,:num]
        log = LogisticRegression(solver='newton-cg')
        model = log.fit(x_reduced_train[:,:num], y_train)
        y_pred = log.predict(x_reduced_test)

        return y_pred

    #'MODIFIED'
    def draw_pca_graph(self, mse):
        '''
        Given the list of mean square error and plot it

        Input:
          mse: list, mean square errors of each component

        Return
        '''

        plt.plot(np.array(mse), '-v')
        plt.xlabel('Number of principal components in regression')
        plt.ylabel('MSE')
        plt.title('Pricipal component and mean square errors')
        plt.xlim(xmin=-1)
        plt.show()
    
        return        


    def get_confusion_matrix(self, y_test, y_pred):
        '''
        Given the testing set and prediction for y (categorical) and return
        a confusion matrix.

        Input:
          y_test: series, testing set for y
          y_pred: series, prediction for y

        Return: numpy array
        '''

        result_matrix = confusion_matrix(y_test, y_pred)

        return result_matrix

    def get_precision_table(self, y_test, y_pred):
        '''
        Given the testing set and prediction for y (categorical) and return
        print out a classification report table.

        Input:
          y_test: series, testing set for y
          y_pred: series, prediction for y

        Return
        '''
        table = classification_report(y_test, y_pred)

        return table

    def get_portfolio_detail(self, test_in, y_pred):
        '''
        Given the price percentage increase for testing set and prediction, 
        return the size of portfolio and expected return. 

        Input:
          test_in: series, price percentage increase for testing set
          y_pred: series, prediction for buying or not 

        Return: tuple
        '''
        
        y_port = test_in[y_pred == 1]
        shape = y_port.shape[0]

        return y_port.shape[0], y_port.mean()


#write pcr prediction to json file, you can harcode y_pred
#by using get_prediction function and setting differnt number of pc
#harcode to k_fold =2, it should be larger than 2
PCR = PCR_mod(2, X_TRAIN, Y_TRAIN, X_TEST, Y_TEST, TEST_IN)
y_pred_pcr = PCR.y_pred
PCR_mod = pd.DataFrame(y_pred_pcr, columns = ['PCR'])
PCR_mod.to_json('PCR_mod.json', orient='values')



#PLS
class PLS_mod:

    def __init__(self, k, x_train, y_train, x_test, y_test, test_in):
        '''
        Construct a partial least square regression model on the 
        data passed. 

        Input:
          k: integer, >=2, parameter for cross validation to calculate 
             mean square error for each principal component
          x_train: dataframe, training set for predictors
          y_train: series, training set for dependet variable
          x_test: dataframe, testing set for predictors
          y_test: series, testing set for dependent variable
          test_in: series, price percentage increase in testing set

        Return:
          mse: list, the list of mean square error for each principal 
               component
          best_n: the number of component with least mean square error
          min_error: the minimum mean square error
          y_pred: series, best prediction made based on all given attributes
          confusion_matrix: numpy array, the confusion matrix for y_pred and 
                            y_test
          report: string, the classification report 
          prot_shape: integer, the size of portfolio predicted from testing 
                      set
          exp_rv: float, the expected percentage increase from the portfolio
        '''

        self.k_fold = k
        self.x_train = x_train
        self.y_train = y_train
        self.x_test = x_test
        self.y_test = y_test
        self.test_in = test_in
        self.mse, self.best_n, self.min_error = self.find_best_pls(x_train, \
                                                                   y_train)
        self.graph = self.draw_pls_graph(self.mse)
        self.y_pred = self.get_prediction(self.best_n, x_train, y_train, \
        	                              x_test)
        self.port_shape, self.exp_rv = \
                    self.get_portfolio_detail(self.test_in, self.y_pred)


    #'MODIFIED'
    def find_best_pls(self, x_train, y_train):
        '''
        Get the number of componet which give minumum mean square error
        from the data for x and y

        Input:
          x_trian: x_train: dataframe, the data for x training set
          y_train: series, the data for y training set

        Return: list, integer
        '''

        kf_10 = KFold(n_splits= self.k_fold, shuffle=False, random_state=1)
        mse = []
        for i in np.arange(1, x_train.shape[1]):
            pls = PLSRegression(n_components=i)
            score = cross_val_score(pls, scale(x_train), y_train, \
                                cv=kf_10, scoring='neg_mean_squared_error').mean()
            mse.append(-score)
        min_error = min(mse)
    
        return mse, mse.index(min_error) + 1, min_error  

    
    #"MODIFIED"
    def get_prediction(self, num, x_train, y_train, x_test):
        '''
        Get the prediction based from the training set and testing set

        Input:
          num: integer, the number of principal components to make prediction
          x_train: dataframe, the data for x training set
          y_train: series, the data for x training set
          x_test: dataframe, the data for x testing set

        Return: series
        '''
    
        pls = PLSRegression(n_components = num)
        pls.fit(scale(x_train), y_train)
        y_pred = pls.predict(scale(x_test))
        y_pred = np.reshape(y_pred, y_pred.shape[0])

        return y_pred
        '''
        pls = PLSRegression(n_components = n_pls + 1) #100
        pls.fit(scale(X_train), y_train)
        y_pred_pls = pls.predict(scale(X_test))
        y_pred_pls = np.reshape(y_pred_pls, y_pred_pls.shape[0])
        y_port = y_test_in[y_pred_pls >= .5]
        '''

    #'MODIFIED'
    def draw_pls_graph(self, mse):
        '''
        Given the list of mean square error and plot it

        Input:
          mse: list, mean square errors of each component

        Return
        '''

        plt.plot(np.array(mse), '-v')
        plt.xlabel('Number of principal components in regression')
        plt.ylabel('MSE')
        plt.title('Pricipal component and mean square errors')
        plt.xlim(xmin=-1)
        plt.show()
    
        return        


    def get_portfolio_detail(self, test_in, y_pred):
        '''
        Given the price percentage increase for testing set and prediction, 
        return the size of portfolio and expected return. 

        Input:
          test_in: series, price percentage increase for testing set
          y_pred: series, prediction for buying or not 

        Return: tuple
        '''
        
        y_port = test_in[y_pred >= .5]

        return y_port.shape[0], y_port.mean()


#write pls prediction to json file, you can hardcode number of principal
#component by using get_prediction function
#harcode to k_fold =2, it should be larger than 2
PLS = PLS_mod(2, X_TRAIN, Y_TRAIN, X_TEST, Y_TEST, TEST_IN)
y_pred_pls = PLS.y_pred
PLS_mod = pd.DataFrame(y_pred_pls, columns = ['PLS'])
PLS_mod['PLS'] = (PLS_mod['PLS'] >= 0.5).astype(int)
PLS_mod.to_json('PLS_mod.json', orient='values')