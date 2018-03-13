import numpy as np
import pandas as pd
import json
from sklearn.metrics import classification_report, confusion_matrix, \
                            mean_squared_error
from sklearn.ensemble import RandomForestClassifier, \
                            GradientBoostingClassifier, BaggingClassifier

#Random Forest

class RandomForest_mod:

    def __init__(self, max_num, x_train, y_train, x_valid, y_valid, x_test, \
                 y_test, test_in):
        '''
        Construct a random forest model on the data passed. 

        Input:
          max_num: integer, maximum number of features in the tree
          x_train: dataframe, training set for predictors
          y_train: series, training set for dependet variable
          x_valid: dataframe, validation set for predictors
          y_valid: series, validation set for dependent variable
          x_test: dataframe, testing set for predictors
          y_test: series, testing set for dependent variable
          test_in: series, price percentage increase in testing set

        Return:
          x_total_train: the whole 'training' set for x to get prediction 
                         combining training set and validation set
          x_total_train: the whole 'training' set for y to get prediction 
                         combining training set and validation set
          best_n: integer, the number of maximum feature to get minimum error 
                  rate for y = 1 comparing training set and validation set
          min_error: float, the minimum error rate mentioned above
          var_importance: a list of tuple recording the ranking of importance
                          of predictors, predictor names and variance 
                          explained
          y_pred: series, best prediction made based on all given attributes
          confusion_matrix: numpy array, the confusion matrix for y_pred and 
                            y_test
          report: string, the classification report 
          prot_shape: integer, the size of portfolio predicted from testing 
                      set
          exp_rv: float, the expected percentage increase from the portfolio
        '''
        
        self.max_num = max_num
        self.x_train = x_train
        self.y_train = y_train
        self.x_valid = x_valid
        self.y_valid = y_valid
        self.x_test = x_test
        self.y_test = y_test
        self.test_in = test_in
        self.x_total_train = pd.concat([x_train, x_valid]).reset_index(drop=\
        	                                                           True)
        self.y_total_train = pd.concat([y_train, y_valid]).reset_index(drop=\
        	                                                           True)
        self.best_n, self.min_error = self.get_best_feature(x_train.shape[1],\
        	                            x_train, y_train, x_valid, y_valid)
        self.var_importance = self.get_importance_list(self.best_n, x_train, \
                                                       y_train)
        self.y_pred = self.get_prediction(self.best_n, self.x_total_train, \
        	                              self.y_total_train, x_test)
        self.confusion_matrix = self.get_confusion_matrix(self.y_test, \
        	                    self.y_pred)
        self.report = self.get_precision_table(self.y_test, self.y_pred)
        self.port_shape, self.exp_rv = \
                   self.get_portfolio_detail(self.test_in, self.y_pred)


    def get_best_feature(self, num, x_train, y_train, x_valid, y_valid):
        '''
        Return the number of max features in the random forest model
        and the value of the error rate for y = 1 it gets from the 
        training set and validation set.

        Inputs:
          num: integer, the maximum number of max feature
          x_train: dataframe, the data for x training set
          y_train: series, the data for y training set
          x_valid: dataframe, the data for x validation set
          y_valid: series, the data for y validation set

        Return: tuple
        '''
        min_error = 1
        f_num = 1
        for i in range(1, num):
            tree_random = RandomForestClassifier(n_estimators = 100, \
                          max_features = i, bootstrap = True,\
                          oob_score = True, random_state = 0)
            tree_random.fit(x_train, y_train)
            y_pred = tree_random.predict(x_valid)
            error = (y_valid != y_pred).astype(int)
            avg = error[y_pred == 1].mean()
            if avg < min_error:
                f_num = i
                min_error = avg
        
        return f_num, min_error


    def get_prediction(self, num, x_train, y_train, x_test):
        '''
        Given the number of max_features, training and testing sets to
        get the prediction for y.

        Input:
          num: integer, the maximum number of neighbours
          x_train: dataframe, training set for x
          y_train: series, training set for y
          x_test: dataframe, testing set for x

        Return: series
        '''

        tree_random = RandomForestClassifier(n_estimators = 100, \
                                             max_features = num, \
                                             bootstrap = True, \
                                             oob_score = True, 
                                             random_state = 25)
        tree_random.fit(x_train, y_train)
        y_pred = tree_random.predict(x_test)

        return y_pred

    def get_importance_list(self, num, x_train, y_train):
        '''
        Get the list ranking variable importane based on the number of 
        features and store them in a tuple(rank, variable, variance explained,
        testing set and validation set passed. 

        Inputs:
          num: integer, the maximum number of max feature
          x_train: dataframe, the data for x training set
          y_train: series, the data for y training set

        Return: list of tuples
        '''
        
        rank_list = []
        tree_random = RandomForestClassifier(n_estimators = 100, \
                                             max_features = num, \
                                             bootstrap = True, \
                                             oob_score = True, 
                                             random_state = 25)
        tree_random.fit(x_train, y_train)
        features = x_train.columns
        importances = tree_random.feature_importances_  
        ranks = np.argsort(importances)[::-1] 
        for f in range(x_train.shape[1]):
            rank_list.append((f + 1, features[ranks[f]], \
                              importances[ranks[f]]))
        
        return rank_list

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

        return y_port.shape[0], y_port.mean()


RF = RandomForest_mod(X_TRAIN.shape[1], X_TRAIN, Y_TRAIN, X_VALID, Y_VALID, \
                      X_TEST, Y_TEST, TEST_IN)
RF_model = pd.DataFrame(RF.y_pred, columns = ['RF'])
RF_model.to_json('RF_mod.json', orient='values')


#Bagging
class BAGGING_mod:

    def __init__(self, min_num, max_num, x_train, y_train, x_valid, y_valid, \
                 x_test, y_test, test_in):
        '''
        Construct a random forest model on the data passed. 

        Input:
          min_num: integer, minimum number of samples to draw in each estimator
          max_num: integer, maximum number of samples to draw in each estimator
          x_train: dataframe, training set for predictors
          y_train: series, training set for dependet variable
          x_valid: dataframe, validation set for predictors
          y_valid: series, validation set for dependent variable
          x_test: dataframe, testing set for predictors
          y_test: series, testing set for dependent variable
          test_in: series, price percentage increase in testing set

        Return:
          x_total_train: the whole 'training' set for x to get prediction 
                         combining training set and validation set
          x_total_train: the whole 'training' set for y to get prediction 
                         combining training set and validation set
          best_n: integer, the number of maximum feature to get minimum error 
                  rate for y = 1 comparing training set and validation set
          min_error: float, the minimum error rate mentioned above
          y_pred: series, best prediction made based on all given attributes
          confusion_matrix: numpy array, the confusion matrix for y_pred and 
                            y_test
          report: string, the classification report 
          prot_shape: integer, the size of portfolio predicted from testing 
                      set
          exp_rv: float, the expected percentage increase from the portfolio
        '''
        
        self.min_num = min_num
        self.max_num = max_num
        self.x_train = x_train
        self.y_train = y_train
        self.x_valid = x_valid
        self.y_valid = y_valid
        self.x_test = x_test
        self.y_test = y_test
        self.test_in = test_in
        self.x_total_train = pd.concat([x_train, x_valid]).reset_index(drop=\
                                                                     True)
        self.y_total_train = pd.concat([y_train, y_valid]).reset_index(drop=\
                                                                     True)
        self.best_n, self.min_error = self.get_best_sample(min_num, max_num, \
                                                           x_train, y_train, \
                                                           x_valid, y_valid)
        self.y_pred = self.get_prediction(self.best_n, self.x_total_train, \
                                        self.y_total_train, x_test)
        self.confusion_matrix = self.get_confusion_matrix(self.y_test, \
                              self.y_pred)
        self.report = self.get_precision_table(self.y_test, self.y_pred)
        self.port_shape, self.exp_rv = \
                   self.get_portfolio_detail(self.test_in, self.y_pred)


    def get_best_sample(self, min_num, max_num, x_train, y_train, x_valid, \
                        y_valid):
        '''
        Return the number of sample size in the bagging model and the 
        smallest value of the error rate for y = 1 it gets from the 
        training set and validation set.

        Inputs:
          min_num: integer, the minimum number of sample size
          max_num: integer, the maximum number of sample size
          x_train: dataframe, the data for x training set
          y_train: series, the data for y training set
          x_valid: dataframe, the data for x validation set
          y_valid: series, the data for y validation set

        Return: tuple
        '''

        min_error = 1
        f_num = 1
        if (min_num < max_num) and (max_num < x_train.shape[0]):
            for i in range(min_num, max_num + 1):
                bag_tree = BaggingClassifier(n_estimators = 500, \
                                             max_samples = i,
                                             max_features = \
                                             x_train.shape[1], \
                                             bootstrap = True, \
                                             oob_score = True, \
                                             random_state = 0)
                bag_tree.fit(X_train, y_train)
                y_pred = bag_tree.predict(X_test)
                error = (y_test != y_pred).astype(int)
                avg = error[y_pred == 1].mean()
                if avg < min_error:
                    f_num = i
                    min_error = avg
        
        return f_num, min_error


    def get_prediction(self, num, x_train, y_train, x_test):
        '''
        Given the number of max_samples, training and testing sets to
        get the prediction for y.

        Input:
          num: integer, the maximum number of neighbours
          x_train: dataframe, training set for x
          y_train: series, training set for y
          x_test: dataframe, testing set for x

        Return: series
        '''

        bag_tree = BaggingClassifier(n_estimators = 500, \
                                     max_features = x_train.shape[1],
                                     max_samples = num, bootstrap = True, \
                                     oob_score = True, random_state = 0)
        bag_tree.fit(x_train, y_train)
        y_pred = bag_tree.predict(x_test)

        return y_pred

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

        return y_port.shape[0], y_port.mean()


BAG = BAGGING_mod(1, X_TRAIN.shape[0], X_TRAIN, Y_TRAIN, X_VALID, Y_VALID, \
                  X_TEST, Y_TEST, TEST_IN)
BAG_model = pd.DataFrame(BAG.y_pred, columns = ['BAGGING'])
BAG_model.to_json('BAGGING_mod.json', orient='values')


#Boosting
class BOOSTING_mod:

    def __init__(self, x_train, y_train, x_valid, y_valid, x_test, \
                 y_test, test_in):
        '''
        Construct a boosting model on the data passed. 

        Input:
          x_train: dataframe, training set for predictors
          y_train: series, training set for dependet variable
          x_valid: dataframe, validation set for predictors
          y_valid: series, validation set for dependent variable
          x_test: dataframe, testing set for predictors
          y_test: series, testing set for dependent variable
          test_in: series, price percentage increase in testing set

        Return:
          x_total_train: the whole 'training' set for x to get prediction 
                         combining training set and validation set
          x_total_train: the whole 'training' set for y to get prediction 
                         combining training set and validation set
          var_importance: a seires recording the importance of variables 
                          in boosting model's learning process
          y_pred: series, best prediction made based on all given attributes
          confusion_matrix: numpy array, the confusion matrix for y_pred and 
                            y_test
          report: string, the classification report 
          prot_shape: integer, the size of portfolio predicted from testing 
                      set
          exp_rv: float, the expected percentage increase from the portfolio
        '''

        self.x_train = x_train
        self.y_train = y_train
        self.x_valid = x_valid
        self.y_valid = y_valid
        self.x_test = x_test
        self.y_test = y_test
        self.test_in = test_in
        self.x_total_train = pd.concat([x_train, x_valid]).reset_index(drop=\
                                                                     True)
        self.y_total_train = pd.concat([y_train, y_valid]).reset_index(drop=\
                                                                     True)
        
        self.var_importance = self.get_importance(x_train, y_train)
        self.y_pred = self.get_prediction(self.x_total_train, \
                                          self.y_total_train, x_test)
        self.confusion_matrix = self.get_confusion_matrix(self.y_test, \
                              self.y_pred)
        self.report = self.get_precision_table(self.y_test, self.y_pred)
        self.port_shape, self.exp_rv = \
                   self.get_portfolio_detail(self.test_in, self.y_pred)


    def get_importance(self, x_train, y_train):
        '''
        Return a series recording importance of x variables from the training
        set. 

        Input:
          x_train: dataframe, training set for x
          y_train: series, training set for y

        Return: a series
        '''

        boost = GradientBoostingClassifier(n_estimators = 500, \
                                           learning_rate = 0.01, \
                                           max_depth = 2, random_state=1)
        boost.fit(x_train, y_train)
        feature_importance = boost.feature_importances_*100
        var_impor = pd.Series(feature_importance, index = \
                              x_train.columns).sort_values(inplace=False)

        return var_impor  


    def get_prediction(self, x_train, y_train, x_test):
        '''
        Given the number of max_samples, training and testing sets to
        get the prediction for y.

        Input:
          x_train: dataframe, training set for x
          y_train: series, training set for y
          x_test: dataframe, testing set for x

        Return: series
        '''

        boost = GradientBoostingClassifier(n_estimators = 500, \
                                           learning_rate = 0.01, \
                                           max_depth = 2, random_state=1)
        boost.fit(x_train, y_train)
        y_pred = boost.predict(x_test)

        return y_pred

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

        return y_port.shape[0], y_port.mean()


BOOST = BOOSTING_mod(X_TRAIN, Y_TRAIN, X_VALID, Y_VALID, X_TEST, Y_TEST, \
                     TEST_IN)
BOOST_model = pd.DataFrame(BOOST.y_pred, columns = ['BOOSTING'])
BOOST_model.to_json('BOOSTING_mod.json', orient='values')