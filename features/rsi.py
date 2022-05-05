# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 00:08:43 2022

@author: ghrit
"""

import pandas as pd

class RSI:
    """
    A class to calculate the relative strength index (RSI). It is a momentum indicator
    used in technical analysis that measures the magnitude of recent price changes to 
    evaluate overbought or oversold conditions in the price of a stock or other asset. 
    """
    def __init__(self, period: int = 14):
        """
        Initialize RSI index class object attributes and methods

        Parameters
        ----------
        period : int, optional
            Window over which RSI is calculated. The default is 14.

        Returns
        -------
        None.

        """
        self.period = period
        self.previous_avg=0
        self.rsi=None
        self.__indicator = self.get_rsi
        self.counter=1
        self.data_fetcher = None
    
    def fetch_stock_data(self,stock: str,start_date: str) -> None:
        """
        Get data for 1 year from required start date to get accurate RSI

        Parameters
        ----------
        stock : str
            NSE Stock symbol.
        start_date : str
            Date string in dd/mm/yyyy format.

        Returns
        -------
        None

        """
        
        start_date = pd.to_datetime(start_date,dayfirst=True) # Convert to a datetime object
        actual_start_date = start_date + pd.offsets.DateOffset(years=-1) # get at  least one year prior data
        actual_start_date = actual_start_date.strftime('%d/%m/%Y') # Convert back to string for data fetcher
        self.stock_data = self.data_fetcher(stock,actual_start_date)
        
    def get_indicator_values(self,stock: str, sd: str,ed: str)-> pd.DataFrame:
        """
        Interface function implemented to collect the result of indicator calculations.

        Parameters
        ----------
        stock : str
          symbol of stock.
        sd : str
          start date from which RSI is asked
        ed : str
          end date till which RSI is asked.
  
        Returns
        -------
        Pandas Dataframe
          Returns a dataframe with columns [Date, indicator] with calculated RSI values.

        """
        self.get_rsi(stock,sd,ed)
        return self.rsi
    
    def get_rsi(self,stock: str,start_date: str, end_date:str) -> pd.DataFrame:
        """
        Calculate RSI for all the dates in the self.stock_data and store it in self.rsi

        Parameters
        ----------
        stock : str
          stock symbol for which RSI is being calculated.
        start_date : str
          The staring date of period for which RSI is being indicated.
        end_date : str
          The ending date of period for which RSI is being indicated.
  
        Returns
        -------
        Pandas Dataframe
          returns dataframe with calculated RSI values.
  
        """
        self.fetch_stock_data(stock,start_date) # get required data for rsi calculation
        print(self.stock_data)
        
        # RSI step one calculation for first window
        initial_period = list(self.stock_data["Close"].iloc[:self.period+1])
        self.previous_avg=self.get_averages_over_window(initial_period,initial = True)
        
        #RSI step 2 calculation for consequent windows
        rsi = self.stock_data["Close"].iloc[1:].rolling(self.period).apply(self.smooth_average,args=())
        print('RSI: ',rsi)
        
        rsi = rsi.rename("RSI")
        self.rsi = pd.concat([self.stock_data["Date"],rsi],axis=1)
        self.rsi = self.rsi[self.rsi["Date"]>=pd.to_datetime(start_date, dayfirst=True)] # Truncate before start date
        
        self.previous_avg=0 #reset average
        
        return self.rsi
    
    def get_averages_over_window(self,period_data: pd.Series ,initial: bool =False):

        """
        Calculates average gain and average loss of the closing prices in the given period.

        Parameters
        ----------
        period_data : Panda series
            Stock closing price for only given period..
        initial : boolean, optional
          If True, RSI for first period of data is being calculated.Returns the non smooth, simple average.
          IF False, smoothened average is returned. The default is False.
  
        Returns
        -------
        average_gain: float
          Average gain in the 14 day period on closing price.
        average_loss: float
          Average loss in the 14 day period on closing price.
  
        """
        prices = list(period_data)
        period = len(prices)
        gains = []
        losses = []
        for i in range(1,len(prices)):
            curr=prices[i]
            prev = prices[i-1]
            if curr<prev:
                gains.append(0)
                losses.append(abs(curr-prev))
            if curr>=prev:
                gains.append(abs(curr-prev))
                losses.append(0)
        
        if initial:
            return sum(gains)/(period-1), sum(losses)/(period)-1
        
        average_gain = ((self.previous_avg[0]*(period-1))+gains[-1])/period
        average_loss = ((self.previous_avg[1]*(period-1))+losses[-1])/period
        return average_gain,average_loss
    def smooth_average(self,period_data):
        # currdate = self.stock_data['Date'].iloc[self.counter]
        # # print("Current Date: ",currdate, self.counter)
        # if pd.to_datetime('01/04/2020',dayfirst=True)==currdate:
        #   print("Oh no",self.counter, period_data)
        # if(self.counter==248):
        #   print(self.stock_data.loc[self.stock_data["Date"]==pd.to_datetime('02/04/2020',dayfirst=True)])
        # self.counter=self.counter+1
        
        """
        Function that is called for each rolling 14 day period to do the RSI calculation for that period.

        Parameters
        ----------
        period_data : Panda series
            Stock closing price for only given period.

        Returns
        -------
        rsi : float
            Calculated RSI value for the period.

        """
        avg_profit,avg_loss = self.previous_avg= self.get_averages_over_window(period_data,False)
        rsi = 100 - (100/(1+(avg_profit/avg_loss)))
        return rsi