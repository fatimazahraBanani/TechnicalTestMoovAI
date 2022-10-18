#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 16:11:48 2022

@author: fatima-zahrabanani
"""
import seaborn as sns
sns.set_theme(style='darkgrid')

class Visualize:
    
    def __init__(self,df):
        self.df = df
        
        
    def univariate_plot(self,column):
        """
        function which create univariate visualizations of columns.

        Parameters
        ----------
        column : str
            Column name.

        Returns
        -------
        None.

        """
        if self.df[column].dtype == "float64":
            chart = sns.kdeplot(self.df[column])
        else:
            chart = sns.countplot(x =column, data = self.df, palette = "Set2")
            chart.set_xticklabels(chart.get_xticklabels(), rotation=45, horizontalalignment='right')

    def box_plot(self,column):
        """
        function which plots box plot of the column depending on the target column.

        Parameters
        ----------
        column : str
            Column name.

        Returns
        -------
        None.

        """
        sns.boxplot(data=self.df, x=column, y="state", palette="Blues",showmeans=True)
        