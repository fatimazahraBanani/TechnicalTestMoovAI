#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 16:11:04 2022

@author: fatima-zahrabanani
"""

from sklearn.tree import DecisionTreeClassifier, export_graphviz, plot_tree, export_text
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt
import pickle
import os 
import pandas as pd
import shap

class Train:
    """
    class containing methods for training the ML model
    """
    
    def __init__(self,project_dir,features,target,target_names,test_size,params= None):
        self.project_dir = project_dir
        csvFile = os.path.join(self.project_dir,"data","processed.csv")
        self.data = pd.read_csv(csvFile)
        self.train = None
        self.test = None
        self.target = target
        self.features = features
        if params == None:
            self.params = {
                'max_depth': [2, 3],
                'min_samples_leaf': [3, 5, 7],
                'criterion': ["gini", "entropy"]
                }
        else:
            self.params = params
        self.model = None
        self.test_size = test_size
        self.target_names = target_names
    
    def split_data(self,test_size):
        self.train, self.test = train_test_split(self.data, test_size= test_size, random_state=1)
        
    def hyperparameter_tuning_training(self):
        dt = DecisionTreeClassifier(random_state=99)
        grid_search = GridSearchCV(estimator=dt, 
                           param_grid=self.params, 
                           cv=4, n_jobs=-1, verbose=1, scoring = "accuracy")
        grid_search.fit(self.train[self.features], self.train[self.target])
        self.model = grid_search.best_estimator_
    
     
        
    def start_training(self):
        self.split_data(self.test_size)
        self.hyperparameter_tuning_training()
        self.plot_tree()
        self.shap_values()
        self.accuracy()
        # save the model to disk
        filename = os.path.join(self.project_dir,"models",'trained_model.sav')
        pickle.dump(self.model, open(filename, 'wb'))
        
    def plot_tree(self):
        
        fig = plt.figure(figsize=(50,35))
        _ = plot_tree(self.model,
                   feature_names=self.features,
                   class_names=self.target_names,
                   filled=True)
        text_representation = export_text(self.model,feature_names=self.features)
        print(text_representation)
        
        
    def shap_values(self):
        fig = plt.figure(figsize=(25,20))
        explainer = shap.TreeExplainer(self.model)
        shap_values = explainer.shap_values(self.train[self.features])
        shap.summary_plot(shap_values,feature_names=self.features,class_inds=[1])
        
    def accuracy(self):
        y_pred = self.model.predict(self.test[self.features])
        accuracy = accuracy_score(self.test[self.target],y_pred)
        print("The accuracy of the model on the test data is: ",accuracy)
        
    
        

