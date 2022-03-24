# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 16:45:14 2022

@author: ghrit
"""

import pickle
import os
import pandas as pd
import numpy as np
import investpy


class DmiIndicator:
    __root_path = os.getcwd()
    __stock_file = ''
    __ind_file= ''
    
    def __init__(self,period=14):
        """
        Initialize RSI index class object attributes and methods
        """
        print(self.__root_path)
        # self.__fetch_stocks()
        self.period = period
        self.previous_avg=0
        self.nse_investing = {"BANKBARODA":"BOB",
                 "BHEL":"BHEL","GAIL":"GAIL",
                 "GMRINFRA":"GMRI",
                 "IDEAEQN":"VODA",
                 "IDFCFIRST" :"IDFB",
                 "NTPC": "NTPC",
                 "PNB":"PNBK","SAIL":"SAIL",
                 "TATAMOTORS":"TAMO"}

    def __fetch_stocks(self):
        """
        Fetch the list of available stocks in database.

        Returns
        -------
        None.

        """
        with open(os.path.join(self.__root_path,'..','beta','data','stock_list.pkl'),'rb') as sfile:
            self.stocks_list = pickle.load(sfile)
        print("Available Stocks: ",self.stocks_list )

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
        # symb = self.nse_investing[stock]
        actual_start_date = pd.to_datetime(start_date, dayfirst=True)
        actual_start_date = actual_start_date + pd.offsets.DateOffset(days=-100)
        actual_start_date = actual_start_date.strftime('%d/%m/%Y')
        actual_end_date = pd.to_datetime(end_date, dayfirst=True)
        actual_end_date = actual_end_date.strftime('%d/%m/%Y')
        # self.stock_data = investpy.get_stock_historical_data(stock=symb,
        #                                 country='India',
        #                                 from_date=actual_start_date,
        #                                 to_date=actual_end_date)
        self.stock_data=self.data_fetcher(stock,actual_start_date, actual_end_date, True)

        # self.stock_data["Date"] = self.stock_data.index
        # self.stock_data = self.stock_data.reset_index(level=0, drop=True)
        print(self.stock_data)

    def dmi_tr(self):
        self.data['trueRange'] = np.NaN
        # print('data + trueRange', self.data)
        x = 1
        while x < len(self.data.index):
            # print('x', x)
            self.data['trueRange'][x] = max((self.data['High'][x]-self.data['Low'][x]), abs(self.data['High'][x]-self.data['Close'][x-1]), abs(self.data['Low'][x]-self.data['Close'][x-1]) )
            x = x + 1

        self.data = self.data.iloc[1: , :].reset_index()
        # print('\ndata with trueRange:', self.data)

    def dmi_positiveDI(self):
        self.data['PDI'] = np.NaN
        for x in self.data.index[1:]:
            if ((self.data['High'][x] - self.data['High'][x-1]) > (self.data['Low'][x-1] - self.data['Low'][x])):
                self.data['PDI'][x] = (self.data['High'][x] - self.data['High'][x-1])
            else:
                self.data['PDI'][x] = 0

        # print('\ndata with PDI:', self.data)
    
    def dmi_negativeDI(self):
        self.data['NDI'] = np.NaN
        for x in self.data.index[1:]:
            if ((self.data['High'][x] - self.data['High'][x-1]) < (self.data['Low'][x-1] - self.data['Low'][x])):
                self.data['NDI'][x] = (self.data['Low'][x-1] - self.data['Low'][x])
            else:
                self.data['NDI'][x] = 0

        # print('\ndata with NDI:', self.data)

    def dmi_smoothening(self, period=14):
        self.data['smoothenedTR'] = np.NaN
        self.data['smoothened+DI'] = np.NaN
        self.data['smoothened-DI'] = np.NaN
        self.data['smoothenedTR'][period] = sum(self.data['trueRange'][1:period])
        self.data['smoothened+DI'][period] = sum(self.data['PDI'][1:period])
        self.data['smoothened-DI'][period] = sum(self.data['NDI'][1:period])
        # print("before dmi_smoothening", self.data)

        for x in self.data.index[period+1:]:
            self.data['smoothenedTR'][x] = (self.data['smoothenedTR'][x-1]*(1-(1/period)))+self.data['trueRange'][x]
            self.data['smoothened+DI'][x] = (self.data['smoothened+DI'][x-1]*(1-(1/period)))+self.data['PDI'][x]
            self.data['smoothened-DI'][x] = (self.data['smoothened-DI'][x-1]*(1-(1/period)))+self.data['NDI'][x]

        # print("after dmi_smoothening", self.data)

    def dmi_ADX(self, period=14):
        self.data['DX'] = np.NaN
        self.data['posDI'] = np.NaN
        self.data['negDI'] = np.NaN
        self.data['ADX'] = np.NaN        
        # print("before dmi_ADX", self.data)

        for x in self.data.index[period:]:
            self.data['posDI'][x] = (self.data['smoothened+DI'][x]/self.data['smoothenedTR'][x])*100
            self.data['negDI'][x] = (self.data['smoothened-DI'][x]/self.data['smoothenedTR'][x])*100        
            self.data['DX'][x] = ((abs(self.data['posDI'][x]-self.data['negDI'][x]))/(abs(self.data['posDI'][x]+self.data['negDI'][x])))*100

        self.data['ADX'][2*period-1] = self.data['DX'][period:2*period-1].mean()
        for x in self.data.index[2*period:]:
            self.data['ADX'][x] = ((self.data['ADX'][x-1]*(period-1))+self.data['DX'][x])/period
        # print("after dmi_ADX", self.data)

    def calculate_dmi(self, stock, start_date=None, end_date=None):

        print("\nChosen stock: ",stock)
        if not start_date:
            start_date = '2020-04-01'
        if not end_date:
            end_date='2021-04-01'
        self.fetch_stock_data(stock, start_date, end_date)
        self.data = self.stock_data
        self.data = self.data[self.data.columns[self.data.columns.isin(['Date', 'Close', 'High', 'Low'])]]
        # print("Raw data: ", self.data)
        self.dmi_tr()
        self.dmi_positiveDI()
        self.dmi_negativeDI()
        self.dmi_smoothening()
        self.dmi_ADX()
        self.dmi = pd.concat([self.data["Date"],self.data["posDI"],self.data["negDI"],self.data["ADX"]],axis=1)
        # self.dmi = self.data[['Date', '+DI', '-DI', 'ADX']].set_index('Date').loc[end_date:start_date]
        self.dmi = self.dmi[self.dmi["Date"]>=pd.to_datetime(start_date, dayfirst=True)]
        # self.dmi.rename(columns = {'ADX':'Indicator'}, inplace = True)

        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        #     print("Data: ", self.dmi ,end="\n\n")

    def get_indicator_values(self, stock, sd, ed):
        self.calculate_dmi(stock, sd, ed)
        return self.dmi

    def get_published_values(self, stock, start_date=None, end_date=None):
        dirc= os.path.dirname(__file__)
        path = os.path.join(dirc, './dmi_data.xlsx')
        stock_data = pd.read_excel(path,sheet_name=stock)
        # print("initial stock_data", stock_data)
        calc_dmi = self.dmi.sort_values(by=["Date"],ascending=False)
        calc_dmi = calc_dmi.dropna()
        stock_data["Date"] = pd.to_datetime(stock_data["Date"])
        stock_data.drop(stock_data[stock_data['Date'] < calc_dmi.iloc[-1]['Date']].index, inplace = True)
        stock_data.drop(stock_data[stock_data['Date'] > calc_dmi.iloc[0]['Date']].index, inplace = True)
        # print("stock_data", stock_data)
        stock_data.rename(columns = {'Adx':'historical'}, inplace = True)
        return stock_data
        
if  __name__ == "__main__":

    dmi = DmiIndicator()
    stock = input("Choose a stock: ").upper()

    dmi.calculate_dmi(stock)