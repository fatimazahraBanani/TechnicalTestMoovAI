#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 16:11:34 2022

@author: fatima-zahrabanani
"""
from sklearn.metrics import accuracy_score
import pickle
import os


class Predict:
    """
    class containing methods to predict data based on trained_model
    """
    def __init__(self,project_dir,test,features,target):
        self.project_dir = project_dir 
        self.test = test
        self.features = features
        self.target = target
    
    def load_model(self):
        filename = os.path.join(self.project_dir,"models",'trained_model.sav')
        self.model = pickle.load(open(filename, 'rb'))
        return self.model
        
    def accuracy(self):
        # To Do: fix bug
        model = self.load_model()
        print(model)
        y_pred = model.predict(self.test[self.features])
        accuracy = accuracy_score(self.test[self.target],y_pred)
        return accuracy

