# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 13:29:34 2022

@author: ghritimport pickle
"""
import os
import pandas as pd
import numpy as np
import investpy


class EmaIndicator:
    
    def __init__(self,period=14):
        """
        Initialize EMA index class object attributes and methods
        """
        self.period = period
        self.previous_avg=0
        self.data_fetcher=None

    def fetch_stock_data(self,stock,start_date=None, end_date=None):
        """
        Sets object attribute 'stock_data' to the data for chosen Stock

        Parameters
        ----------
        stock : String
            Symbol of stock for which to get RSI data.

        Returns
        -------
        None.

        """
        #-------using investpy-----
        actual_start_date = pd.to_datetime(start_date, dayfirst=True)
        actual_start_date = actual_start_date + pd.offsets.DateOffset(days=-75)
        actual_start_date = actual_start_date.strftime('%d/%m/%Y')
        actual_end_date = pd.to_datetime(end_date, dayfirst=True)
        actual_end_date = actual_end_date.strftime('%d/%m/%Y')
        self.stock_data=self.data_fetcher(stock,actual_start_date)
        self.stock_data = self.stock_data.reset_index(level=0, drop=True)
        # print(self.stock_data)
    
    def calculation(self, smoothening, period):
        
        multiplier = smoothening / (1 + period)
        complete = False
        count = 0
        sma_arr = self.data[:period]
        iden = "ema"+str(period)
        self.data[iden] = np.NaN
        self.data[iden][period] = sum(sma_arr['Close'])/period
        count = period + 1
        for x in self.data[iden][period+1:]:

            self.data[iden][count] = (self.data['Close'][count] * multiplier) + (self.data[iden][count-1] * (1 - multiplier))
            count += 1

    def calculate_ema(self, stock, start_date=None, end_date=None):

        print("\nChosen stock: ",stock)
        if not start_date:
          start_date = '2020-04-01'
        if not end_date:
          end_date='2021-04-01'
          
        self.fetch_stock_data(stock, start_date, end_date)
        self.data = self.stock_data.loc[:, ('Date', 'Close')]

        smoothening = 2
        self.calculation(smoothening, 10)
        self.calculation(smoothening, 20)
        self.calculation(smoothening, 50)
        
        # print('interim data', self.data['Date'])
        
        self.ema = pd.concat([self.data['Date'],self.data["ema10"],self.data["ema20"],self.data["ema50"]],axis=1)
        self.ema = self.ema[self.ema['Date']>=pd.to_datetime(start_date)]
        
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        #     print("Data: ", self.ema ,end="\n\n")
        
    def get_indicator_values(self, stock, sd, ed):
        self.calculate_ema(stock, sd, ed)
        return self.ema

if  __name__ == "__main__":

    ema = EmaIndicator()
    stock = input("Choose a stock: ").upper()
    start_date = input("Enter start date (in YYYY-MM-DD format): ")
    end_date = input("Enter end date (in YYYY-MM-DD format): ")
    
    ema.calculate_ema(stock, start_date, end_date)

