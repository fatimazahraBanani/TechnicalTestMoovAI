#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 16:09:46 2022

@author: fatima-zahrabanani
"""
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import pycountry
import os
import re

class MakeDataset:
    """
    class responsible of turning the original dataset
    into a clean one. It is achieved by eliminating unconsistency 
    in the columns, droping some rows with nan values if they can't be filled 
    otherwise filling the missing values and by checking that the 
    relationships between columns in the same row are respected.
    """
    def __init__(self,project_dir,missing_values_percent = 85, html_parent_child=None, allowed_values = None):
        # directory of the project
        self.project_dir = project_dir
        
        # create original dataframe from csvFile
        csvPath = os.path.join(self.project_dir,"data","original.csv")
        self.df = pd.read_csv(csvPath)
        
        # rename columns by deleting extra space
        self.df.rename(columns={col : col.strip().replace(" ","_") for col in list(self.df.columns)},inplace = True)
        
        # maximum limit of percentage of missing values in a column
        self.missing_values_percent = missing_values_percent
        
        # dictionary used to select the options of certain values from html files
        # if not specified the dictionary is created manually
        # keys -> values:
            # column -> (parent tag, child tag)
        if html_parent_child == None:
            self.html_parent_child = dict()
            self.html_parent_child["category"]=self.html_parent_child["main_category"]=self.html_parent_child["currency"] = ('select','option')
            self.html_parent_child["country"] = ('ul','li')
        else:
            self.html_parent_child = html_parent_child
            
        # dictionary used for allowed_values of certain columns
        # keys -> values:
            # "numerical" -> columns' indices which values should be numerical
            # "dateTime" -> columns' indices which values should be dateTime
            # "values" -> list of tuples [(column indice, list of allowed values),..]
        self.set_allowed_values(allowed_values)
            
        
        
        
    
    def get_df(self):
        return self.df
    
    def select_allowed_options(self,column):
        """
        function using the html element from the website source code
        which can be found in the references folder, in order to get 
        all the options of a column value.
        
        Parameters
        ----------
        column : str
            column name

        Returns
        -------
        list of options of the column

        """
        # path of the html file with the options of the column
        htmlFile = os.path.join(self.project_dir,"references",column+".txt")
        text_file = open(htmlFile, 'r')
        html = text_file.read()
        
        # parse html
        soup = BeautifulSoup(html,'html.parser')
        parent,child = self.html_parent_child[column]
        subject_options = [i.findAll(child) for i in soup.findAll(parent)]
        subject_options = [[re.sub("<.*?>", "", str(option).replace("&amp;","&")) for option in subject_option] for subject_option in subject_options]
        #close file
        text_file.close()
    
        if column == "country":
            # the options in countries are the names but in the csvFile 
            # they are specified as the 2_alpha code
            # so we turn the names into their coresponding alpha_2 code
            countries = {}
            for country in pycountry.countries:
                countries[country.name] = country.alpha_2
            subject_options = [countries.get(country.replace("the ", ""), 'Unknown code') for country in subject_options[0]]
    
        if column == "currency":
            # only keep the currency 3 characters code which is between parentheses
            subject_options = [value.strip().split('(')[-1][:-1] for value in subject_options[0]]
        
        if column == "main_category":
            subject_options = subject_options[0][1:]
        
        if len(subject_options)==1:
            return subject_options[0]
    
        return subject_options

    
    def set_allowed_values(self,allowed_values = None):
        """
        function manually creating the allowed_values dictionary
        if not specified as a parameter 

        Parameters
        ----------
        allowed_values : Dictionary, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        """
        if allowed_values == None:
            self.allowed_values= dict()
            self.allowed_values["numerical"] = [6,8,10,12]
            self.allowed_values["dateTime"] = [5,7]
            self.allowed_values["values"] = []
            self.allowed_values["values"] .append(
                (2,self.select_allowed_options("main_category") + [item for sublist in self.select_allowed_options("category") for item in sublist]))
            self.allowed_values["values"].append(
                (3,self.select_allowed_options("main_category")))
            self.allowed_values["values"] .append(
                (4,self.select_allowed_options("currency")))
            self.allowed_values["values"].append(
                (9,['failed', 'canceled', 'successful', 
                    'live', 'undefined','suspended']))
            self.allowed_values["values"].append(
                (11,self.select_allowed_options("country")))
            
    
    def remove_basic_anomaly(self):
        """
        function which detects basic anomaly in data and replace 
        non consistent values in columns to nan based on
        self.allowed_values dictionary

        Returns
        -------
        None.

        """
        # non numerical values will be replaced by nan
        cols = self.df.columns[self.allowed_values["numerical"]]
        self.df[cols] = self.df[cols].apply(pd.to_numeric, errors='coerce')
        
        # values not representing time will be replaced by nan
        cols = self.df.columns[self.allowed_values["dateTime"]]
        self.df[cols] = self.df[cols].apply(pd.to_datetime, errors='coerce')
        
        # function that return value if it belongs to the allowed list otherwise return nan
        def is_in_list(value, allowed_values):
            if value in allowed_values:
                return value
            else:
                return np.nan
            
        # values not belonging to the allowed lists will be replaced by nan
        for column_index, allowed_values in self.allowed_values["values"]:
            self.df[self.df.columns[column_index]] = self.df[self.df.columns[column_index]].apply(
                is_in_list, allowed_values=allowed_values)
            
    
    def fill_nans(self):
        """
        function which fills missing values that can be restored 
        from other columns.

        Returns
        -------
        None.

        """
        from forex_python.converter import CurrencyRates
        # fill usd_pledged column based on currency and pledged columns
        c = CurrencyRates()
        self.df['usd_pledged'] = self.df.apply(lambda row: c.convert(row["currency"],'USD',row["pledged"], row["deadline"]) if np.isnan(row['usd_pledged']) else row['usd_pledged'], axis=1)
            
        # fill state based on goal and pledged columns
        self.df['state'] = self.df.apply(lambda row: "successful" if (row['goal'] <= row['pledged']) else "failed", axis=1)
    
    def remove_unnecessary_columns(self):
        """
        function which drops columns with higher percentage 
        than the attribute missing_values_percent.

        Returns
        -------
        None.

        """
        cols = []
        
        # check the percentage of missing values for each column
        for i in range(0,len(self.df.columns)):
            missing_percent = (self.df.iloc[:,i].isna().sum()*100)/len(self.df)
            if missing_percent > self.missing_values_percent:
                cols.append(i)
                
        self.df.drop(self.df.columns[cols], axis=1, inplace = True)
        
    def remove_unnecessary_rows(self):
        """
        function which drops unnecessary rows based on previous analysis.
        
        Returns
        -------
        None.

        """
        # delete rows with state "canceled","live","suspended" 
        self.df = self.df[self.df["state"].isin(["failed","successful","undefined",np.nan])]
        # delete rows with no category
        self.df = self.df[self.df["category"].notna()]
        
    
    def remove_advanced_anomaly(self):
        """
        function which removes advanced anomaly in data based 
        on relationships between columns.

        Returns
        -------
        None.

        """
        main_categories = self.select_allowed_options("main_category")
        categories = self.select_allowed_options("category")
        main_sub_categories = {main_categories[i]: categories[i]+[main_categories[i]] for i in range(len(main_categories))}


        # check if compaign period is between 1-60 days
        self.df['campaign_period'] = (self.df['deadline'] - self.df['launched']).dt.total_seconds()
        self.df = self.df[self.df['campaign_period']<= (60*24*60*60)]
        self.df['campaign_period'] = self.df['campaign_period']//86400
        
        # check if category and main_category columns are compatible
        self.df['category'] = self.df.apply(lambda x: x.category if x.category in main_sub_categories[x.main_category] else 
                              x.main_category, axis=1)
    
    
    
    def clean_dataset(self):
        """
        function which turns original dataset into a clean one.

        Returns
        -------
        Pandas dataFrame
            Clean dataframe

        """
        # step 1: removing columns with mostly missing values
        self.remove_unnecessary_columns()
        
        # step 2: removing unconsistent values in each column separately
        self.remove_basic_anomaly()
        
        # step 3: removing unnecessary rows based on previous analysis
        self.remove_unnecessary_rows()
        
        # step 4: removing advanced anomaly in data based on some columns relationships
        self.remove_advanced_anomaly()
        
        # step 5: filing nan values which can be deducted from other columns
        self.fill_nans()
        
        # store clean dataframe into a csvFile
        csvPath = os.path.join(self.project_dir,"data","clean.csv")
        self.df.to_csv(csvPath)
        print("Cleaning is Done. You can find the csvFile in data/clean.csv file")

        return self.df
    
    def get_clean_df(self):
        """
        function which return cleaned dataframe if the clean file exists in the data folder

        Returns
        -------
        Pandas dataFrame
            Clean dataFrame if exists otherwise None.

        """
        csvPath = os.path.join(self.project_dir,"data","clean.csv")
        if os.path.exists(csvPath):
            return pd.read_csv(csvPath)
        else:
            print("The clean version of data doesn't exist, you have to run Data Wrangling section")
            return None