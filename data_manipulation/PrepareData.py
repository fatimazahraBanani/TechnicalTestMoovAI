#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 15 08:25:53 2022

@author: fatima-zahrabanani
"""

import pandas as pd
import numpy as np

class CleanData:
    def __init__(self, df):
        self.df = df
        
    def missing_values(self,percent):
        """
        function that drops columns for which the percentage 
        of missing values is strictly greater than parameter
        percent 
        
        parameters:
            percent = threshold of percentage of missing values
        """   
        
        cols = []
        
        # check the percentage of missing values for each column
        for i in range(0,len(self.df.columns)):
            missing_percent = (self.df.iloc[:,i].isna().sum()*100)/len(self.df)
            if missing_percent > percent:
                cols.append(i)
                
        self.df.drop(self.df.columns[cols], axis=1, inplace = True)
        
        
    def remove_basic_anomaly(self,params):
        """
        function that detect basic anomaly in data and replace 
        non consistent values in columns to nan based on
        params dictionary
        
        parameters:
            params = dictionary with keys -> values as follows:
                "numerical" -> list of indices of columns supposed to be numerical
                "dataTime"  -> list of indices of columns supposed to be datetime
                "allowedValues" -> list of tuples of (column's indice,allowed values)
        """
        
        # non numerical values will be replaced by nan
        cols = self.df.columns[params["numerical"]]
        self.df[cols] = self.df[cols].apply(pd.to_numeric, errors='coerce')
        
        # values not representing time will be replaced by nan
        cols = self.df.columns[params["dateTime"]]
        self.df[cols] = self.df[cols].apply(pd.to_datetime, errors='coerce')
        
        # function that return value if it belongs to the allowed list otherwise return nan
        def is_in_list(value, allowed_values):
            if value in allowed_values:
                return value
            else:
                return np.nan
            
        # values not belonging to the allowed lists will be replaced by nan
        for column_index, allowed_values in params["allowedValues"]:
            self.df[self.df.columns[column_index]] = self.df[self.df.columns[column_index]].apply(
                is_in_list, allowed_values=allowed_values)
            
    def remove_advanced_anomaly(self,main_sub_dictionary):
    
        
        
        from forex_python.converter import CurrencyRates
        
        # fill state based on goal and pledged columns
        self.df['state'] = self.df.apply(lambda row: "successful" if (row['goal'] <= row['pledged']) else "failed", axis=1)
        
        # check if compaign period is between 1-60 days
        self.df['compaign_period'] = (self.df['deadline'] - self.df['launched']).dt.total_seconds()
        
        # check if category and main_category columns are compatible
        self.df['category'] = self.df.apply(lambda x: x.category if x.category in main_sub_dictionary[x.main_category] else 
                              x.main_category, axis=1)
        
        # fill usd_pledged column based on currency and pledged columns
        c = CurrencyRates()
        self.df['usd_pledged'] = self.df.apply(lambda row: c.convert(row["currency"],'USD',row["pledged"], row["deadline"]) if np.isnan(row['usd_pledged']) else row['usd_pledged'], axis=1)
        
        
        
        
    
        
        
        