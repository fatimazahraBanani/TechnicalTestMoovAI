#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 16:11:48 2022

@author: fatima-zahrabanani
"""
import seaborn as sns
sns.set_theme(style='darkgrid')
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

class Visualize:
    """
    class containing methods to visualize the data inside the dataFrame
    """
    
    def __init__(self,df,project_dir):
        self.df = df
        self.project_dir = project_dir
        self.figures_dir = os.path.join(self.project_dir,"report","figures")
        
        
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
        imageFile = os.path.join(self.figures_dir,column+'_univariate.png')
        plt.savefig(imageFile)
        
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
        imageFile = os.path.join(self.figures_dir,column+'_box.png')
        plt.savefig(imageFile)
        
    def bivariate_plot(self,column,nbins = None):
        """
        function which create bivariate visualizations of categorical columns.

        Parameters
        ----------
        column : str
            Column name.
        nbins: int
            Number of bins if the column is numerical

        Returns
        -------
        None.

        """
        if self.df[column].dtype == "float64": 
            mini = self.df[column].min()
            maxi = self.df[column].max()
            bins = np.linspace(mini, maxi, num=nbins+1)
            labels = [mini+(i/nbins)*maxi-mini for i in range(nbins)]
            self.df['binned'] = pd.cut(self.df[column], bins=bins, labels=labels)
            df_grouped = self.df.groupby('binned')["state"].value_counts(normalize=True).unstack("state")
        
        # ToDo : try to fix the problem
        elif self.df[column].dtype == "datetime64": 
            self.df['month'] = self.df[column].dt.strftime('%b')
            df_grouped = self.df.groupby('month')["state"].value_counts(normalize=True).unstack("state")
            
        else:
            df_grouped = self.df.groupby(column)["state"].value_counts(normalize=True).unstack("state")
        
        df_grouped[column] = df_grouped.index
        
        fig = px.bar(df_grouped,  x=["successful", "failed"],y=column)
        fig.show()
        imageFile = os.path.join(self.figures_dir,column+'_bivariate.png')
        fig.write_image(imageFile)
        

        
