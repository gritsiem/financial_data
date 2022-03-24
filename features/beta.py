# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 20:33:56 2021

@author: ghrit 
"""
import os

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels import regression
import investpy


class BetaIndicator:
   
    def __init__(self):
        '''
        Initialize Beta Indicator class with attributes.

        Returns
        -------
        None.
  
        '''
        # Choice of methods to calculate beta (linear reg, covariance)
        self.__methods = {'Linear_Regression':self.beta_linearreg,'Covariance_matrix':self.beta_covariance}
      
        
        # additional inputs for test harness.
        self.index  = 'Nifty 50'
        
        # attribut containing historical data for given stock. It can be set from outside class.
        self.stock_data=None
        self.index_data = None
        self.data_fetcher=None
        
            
    def fetch_data(self,stock: str,index: str,start_date: str,end_date: str)-> None:
        """
        Fetch historical data for stocks and index.
        
        stock fetching moved to outside class. 

        Parameters
        ----------
        stock : string
          NSE symbol for stock for which getting historical data.
        index : string
          Investpy symbol for stock for which getting historical data. currently hardcoded to nifty 50.
        start_date : string
          starting date of range of historical data. dd/mm/yyyy format required for investpy.
        end_date : string
          end date of range of historical data. dd/mm/yyyy format required for investpy.
  
        Returns
        -------
        None.
        
        Stores data in object attributes.
  
        """       
        
        print("start end", start_date,end_date)
        
        # Fetch data for at least a year prior to start date for correct calculation.
        start_date = start_date + pd.offsets.DateOffset(years=-1)
        self.stock_data=self.data_fetcher(stock,start_date)
        
        # API call to investpy for index data
        self.index_data = investpy.indices.get_index_historical_data(index, 'India', start_date.strftime('%d/%m/%Y'), end_date.strftime('%d/%m/%Y'), as_json=False, interval='Daily')
        print(len(self.stock_data),len(self.index_data))
        
        # Investpy uses dates to index. Restructuring according to dataset.
        self.index_data["Date"] =self.index_data.index
        self.index_data = self.index_data.reset_index(level=0, drop=True)

    def __remove_uncommon_dates(self,sdf: pd.DataFrame ,idf: pd.DataFrame) -> (pd.DataFrame, pd.DataFrame) :
        """
      

        Parameters
        ----------
        sdf : Dataframe
          Processed stock data.
        idf : Dataframe
          Processed index data .
  
        Returns
        -------
        sdf : Dataframe
            Stock data only containing common dates with index data.
        idf : Dataframe
          Index data only containing common dates with stock data

        """
        # Find uncommon dates in the stock and index data if any
        only_stock = sdf["Date"].isin(idf["Date"])==False
        only_ind = idf["Date"].isin(sdf["Date"])==False

        # drop those rows
        sdf.drop(sdf[only_stock].index, inplace=True)
        idf.drop(idf[only_ind].index, inplace=True)
                
        return sdf,idf

    def filter_on_dates(self,start: str, end: str):
        """
        Filters stock data and index data to get required range for calculation.
        Currently index data is fetched in class itself as only beta requires it.

        Parameters
        ----------
        start : string
          start date of format dd/mm/yyy.
        end : string
          end date of format dd/mm/yyy..
  
        Returns
        -------
        TYPE
          DESCRIPTION.
        TYPE
          DESCRIPTION.

        """
        #reference variables for stock and index data
        sdf = self.stock_data
        idf = self.index_data
        
        #convert string to Datetime object for dates.
        to_date = pd.to_datetime(end,format='%d/%m/%Y')
        ideal_from_date = pd.to_datetime(start,format='%d/%m/%Y')
        
        # Get difference between data dates and start dates. td(time difference) is list of integers.
        td = (sdf.Date - ideal_from_date).values
        
        # get all values where difference non positive (dates older or equal to start date)
        td = td[td<=pd.Timedelta(0)]
        
        #if no such dates, then your starting date i out of range and get all data.
        if len(td)==0:
          print("Selected date out of data range. Including all available data.")
          return sdf,idf
        
        #gets index for the value which is closest but older than ideal start date.
        from_index = len(td)-1
        to_index = sdf.loc[sdf.Date<=to_date].index[-1]
        
        print("Including data from date:" , sdf.iloc[from_index].Date,"\nTo Date: ", to_date, sdf.iloc[to_index].Date)
        filtered_sdf, filtered_idf = sdf.iloc[from_index:to_index+1], idf.iloc[from_index:to_index+1]
        return filtered_sdf, filtered_idf

    
    def beta_linearreg(self,stock, index):
        """
        Calculate beta using linear regression.

        Parameters
        ----------
        stock : dataframe
          stock data of n length
        index : index data
          index data of n length.
  
        Returns
        -------
        beta : float
          Calculated Beta value.
  
        """
        
        print("\nUsing Linear Regression:")
        stock_return = stock['Close'].pct_change()[1:]
        index_return = index['Close'].pct_change()[1:]
        
        x = sm.add_constant(index_return.values)
        y = stock_return.values
        
        #x = x [:, 1]
        model = regression.linear_model.OLS(y,x).fit()
        beta = model.params[1]
        
        return beta

        
    def beta_covariance(self,stock, index):
        """
        Calculates beta using direct matrix operations.

        Parameters
        ----------
        stock : dataframe
          stock data of n length
        index : index data
          index data of n length.
  
        Returns
        -------
        float
        
        Beta
  
        """
        print("\nUsing Covariance Matrix Method:")
        stock_return = stock['Close'].pct_change()[1:]
        index_return = index['Close'].pct_change()[1:]
        
        # first column is the market
        X = np.expand_dims(index_return.values,axis=1)
        # prepend a column of ones for the intercept
        X = np.concatenate([np.ones_like(X), X], axis=1)
        # matrix algebra
        b = np.linalg.pinv(X.T.dot(X)).dot(X.T).dot(stock_return.values)
        
        return b[1]
        
    
    def calculate_beta(self, stock, index,end_date, period_length = None, period_type="Y", Interval = "None", method = None):
        """
      

        Parameters
        ----------
        stock : String
          DESCRIPTION.
        index : TYPE
          DESCRIPTION.
        end_date : TYPE
          DESCRIPTION.
        period_length : TYPE, optional
          DESCRIPTION. The default is None.
        period_type : TYPE, optional
          DESCRIPTION. The default is "Y".
        Interval : TYPE, optional
          DESCRIPTION. The default is "None".
        method : TYPE, optional
          DESCRIPTION. The default is None.
  
        Returns
        -------
        result : TYPE
          DESCRIPTION.

        """
      
      
        if method is None:
            method = list(self.__methods.keys())[0]
            
        beta_method = self.__methods[method]
        index = "Nifty 50"
        
        end_date = pd.to_datetime(end_date,dayfirst=True) +  pd.offsets.DateOffset(days=-1)
        start_date = end_date + pd.offsets.DateOffset(years=-1)+  pd.offsets.DateOffset(days=-1)
        print(end_date.month_name())
        end_date=end_date.strftime('%d/%m/%Y')
        start_date = start_date.strftime('%d/%m/%Y')

        st, ind = self.filter_on_dates(start_date,end_date)
        # print("debug st en after filter: ",st,ind)
        # ind = self.index_data

        st,ind = self.__remove_uncommon_dates(st,ind)

        # print("\n=======\n",st, ind)
        # st, ind = self.stock_data,self.index_data 
        print("Number of data points: ", len(st))
        result =  round(beta_method(st, ind), 2)
        print("Beta: ", result ,end="\n\n")
        return result
        
    def get_indicator_values(self, stock, start,end,index='Nifty 50'):

        val = []
        i=0
        start = pd.to_datetime(start,dayfirst=True)
        end = pd.to_datetime(end,dayfirst=True)
        dates = pd.date_range(start=start,end = end, freq='B')
        self.fetch_data(stock,index,start,end)
        for date in dates:
          if date in self.stock_data.Date.values:
            val.append(self.calculate_beta(stock, index,date))
          else:
            dates = dates.drop(date)
        return pd.DataFrame({'Date':dates, 'Beta':val }) 
      
        
        
        
if  __name__ == "__main__":
    beta = BetaIndicator()

    x = beta.get_indicator_values("BHEL", '05/04/2021','05/04/2021')
    
    