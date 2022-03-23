# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 00:51:57 2021

@author: ghrit
"""

import os
import pandas as pd
import pymongo

class Database:
    def __init__(self):
        self.local_host = 'localhost:27017'
        self.remote_host = ''
        self.url = "mongodb://"+self.local_host + "/?readPreference=primary&directConnection=true&ssl=false"
        self.client = pymongo.MongoClient(self.url) 
        self.db = self.client["niftyfifty"]
        self.stock_data = self.db["stock-data"]
        
    def insert_stock_data(self, stock_data: pd.DataFrame)->None:
        '''

        Parameters
        ----------
        stock_data : pd.DataFrame
          Insert stock data dataframe in the MongoDB database.
  
        Returns
        -------
        None
          DESCRIPTION.
  
        '''
        
        stock_data.Date = stock_data.Date.apply(
          lambda date:pd.to_datetime(date, format="%Y-%m-%d")
          ) #Clean date format
        
        processed_data = stock_data.to_dict('records') # Covert dataframe to dictionary.
        x = self.stock_data.insert_many(processed_data) # Use pymongo function to insert multiple records.
        print('Inserted ',len(x.inserted_ids), ' records.' ) 
        
        # Update the last-update date to today's date
        query={} 
        newvalue = { "$set": { "date": pd.to_datetime('today') } } 
        self.db['last-update'].update_one(query,newvalue)
        
    def get_last_date(self):
        return self.db['last-update'].find()[0]['date']