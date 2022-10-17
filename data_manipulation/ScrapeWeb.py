#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 16 11:16:27 2022

@author: fatima-zahrabanani
"""
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import pycountry
import re
import os

# global dictionary for parent tag and child tag used to find the right attribute options
parent_child_dict = dict()
parent_child_dict["category"]=parent_child_dict["main_category"]=parent_child_dict["currency"] = ('select','option')
parent_child_dict["country"] = ('ul','li')

def select_options(notebook_path, attribute):
    """
    function that gives the list of available option of each attribute
    based on HTML documents of KickStarter website's elements.
    
    Parameters:
        attribute: the attribute for which we want to output the available options
    return:
        list of available options
    """
    #open file
    filename = os.path.join(notebook_path,"Data_Preparation","ElementsHTML","data_"+attribute+".txt")
    #filename = os.path.join("ElementsHTML","data_"+attribute+".txt")
    text_file = open(filename, 'r')
    html = text_file.read()

    soup = BeautifulSoup(html,'html.parser')
    parent,child = parent_child_dict[attribute]
    subject_options = [i.findAll(child) for i in soup.findAll(parent)]
    subject_options = [[re.sub("<.*?>", "", str(option).replace("&amp;","&")) for option in subject_option] for subject_option in subject_options]
    #close file
    text_file.close()
    
    if attribute == "country":
        countries = {}
        for country in pycountry.countries:
            countries[country.name] = country.alpha_2
        subject_options = [countries.get(country.replace("the ", ""), 'Unknown code') for country in subject_options[0]]
    
    if attribute == "currency":
        subject_options = [value.strip().split('(')[-1][:-1] for value in subject_options[0]]
        
    if attribute == "main_category":
        subject_options = subject_options[0][1:]
        
    if len(subject_options)==1:
        return subject_options[0]
    
    return subject_options





