#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 16:10:28 2022

@author: fatima-zahrabanani
"""
from sklearn import preprocessing
import numpy as np
import os

class BuildFeatures:
    """
    class containing methods to build features that can be used with the ML model
    """
    def __init__(self,df,project_dir):
        self.df = df
        self.project_dir = project_dir
        
    def drop_outliers(self,column):
        """
        function that drops outliers based on a column

        Parameters
        ----------
        column : str
            Name of the column studied.


        Returns
        -------
        None.

        """
        Q1 = np.percentile(self.df[column], 25,
                   interpolation = 'midpoint')
 
        Q3 = np.percentile(self.df[column], 75,
                   interpolation = 'midpoint')
        IQR = Q3 - Q1
        # Upper bound
        upper = np.where(self.df[column] >= (Q3+1.5*IQR))
        # Lower bound
        lower = np.where(self.df[column] <= (Q1-1.5*IQR))
 
        # removing the Outliers 
        self.df.drop(upper[0], inplace = True)
        self.df.drop(lower[0], inplace = True)
        
    def drop_unused_columns(self,columns_to_keep):
        """
        function which drops that columns that won't be used for training the ML model

        Parameters
        ----------
        column_to_drop : list
            List of columns that should be dropped.

        Returns
        -------
        None.

        """
        columns = list(self.df.columns)
        for col in columns_to_keep:
            columns.remove(col)
        self.df.drop(columns=columns,inplace = True)
        
    def feature_encoding(self,columns):
        """
        function that encodes the categorical columns given as a parameter

        Parameters
        ----------
        columns : list 
            List of categorical columns to encode.

        Returns
        -------
        None.

        """
        for col in columns:
            self.df[col] = self.df[col].astype('category')
            self.df[col] = self.df[col].cat.codes
            
        
    def target_encoding(self,target):
        """
        function that encodes the target variable

        Parameters
        ----------
        target : str
            target column's name.

        Returns
        -------
        None.

        """
        le = preprocessing.LabelEncoder()
        le.fit(self.df[target])
        self.df[target] = le.transform(self.df[target])        
        print("[0,1] represents :",le.inverse_transform([0,1]))
        
    def save_features(self):
        # store clean dataframe into a csvFile
        csvPath = os.path.join(self.project_dir,"data","processed.csv")
        self.df.to_csv(csvPath)
        print("Feature Engineering is Done. You can find the csvFile in data/processed.csv")
        
        
        
    
        
        
    

