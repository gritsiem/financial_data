import investpy
import os
import pandas as pd
import sys
import time
sys.path.append(os.path.abspath('../'))
from database.database import Database
from features.rsi import RSI
from features.beta import BetaIndicator

class DataFetcher:
    """
    Class to collect stock data and calculate indicators daily.
    """
    def __init__(self):
        """
        Initialize data path, stock config file, and DB connection.

        Returns
        -------
        None.

        """
        self.__config_path = os.path.join(os.path.dirname(__file__))
        # print(self.__data_path)
        self.stocks_data = pd.read_csv(os.path.join(self.__config_path,'config.csv'))
        # print(self.stocks_data)
        self.db = Database()
        
    def fetch_data_for_single(self,stock: str ,start_date: str =None) -> pd.DataFrame:
        """
        Fetches data for single stock for today from investing.com using investpy

        Parameters
        ----------
        stock : string
          Investpy symbol for stock.
        start_date : TYPE, optional
          DESCRIPTION. The default is None: string.
  
        Returns
        -------
        data : TYPE
          Stock data for the day for the given stock.
  
        """
        
        
        end_date = pd.to_datetime('today') #Collect missing data till today.
        if not start_date :
            start_date = end_date + pd.offsets.DateOffset(days=-1) #if no dates given, start data collection from today
        
        if type(start_date)!= str:
            start_date = start_date.strftime('%d/%m/%Y')
        
        end_date =  end_date.strftime('%d/%m/%Y') # Correct formats for investpy API
        print("start end", start_date,end_date)
        if stock in list(self.stocks_data['nse']):
            stock = self.stocks_data.loc[self.stocks_data['nse']==stock]['investpy'].iloc[0]
        self.stock_data = investpy.get_stock_historical_data(stock=stock,
                                        country='India',
                                        from_date=start_date,
                                        to_date=end_date, interval="Daily")
        time.sleep(2) #to avoid IP blocking
        
        # print('Testing',self.stock_data)
        
        # Clean up data from API
        self.stock_data["Date"] =self.stock_data.index
        self.stock_data = self.stock_data.reset_index(level=0, drop=True)
        
        self.stock_data['Stock']=list(self.stocks_data.loc[self.stocks_data['investpy']==stock,'nse'])[0]

        self.stock_data=self.stock_data.iloc[1:].reset_index(level=0, drop=True)
        
        # Columns that we are interested in.
        data = self.stock_data.loc[:,['Date','Stock','Close']]   
        return data

    def fetch(self):
        """
        Fetches Closing prices for required period  for all stocks in config.csv
        and stores in data_today.csv.

        Returns
        -------
        None.

        """
        last_date = self.db.get_last_date()
        start_date =last_date
        investpy_stocks = self.stocks_data['investpy']
        df = pd.DataFrame()
        
        for st in investpy_stocks:
            if df.empty:
                df = self.fetch_data_for_single(st,start_date)
            else:
                df = df.append(self.fetch_data_for_single(st,start_date),ignore_index=True)
        
        df = df.reset_index(level=0, drop=True)
        df.to_csv('data_today.csv',mode='w',header=False,\
                  index=False)
        print(df)
    
    def calculate(self):
        today_data = pd.read_csv('data_today.csv',names=['Date','Stock','Close'])
        self.today = today_data
        print(today_data.Date.iloc[1])
        start_date = pd.to_datetime(today_data.Date.iloc[1]).strftime('%d/%m/%Y')
        end_date = pd.to_datetime(today_data.Date.iloc[-1]).strftime('%d/%m/%Y')
        
        indicators = { RSI: 'RSI', BetaIndicator:'Beta'} # ,
        
        nse_stocks = self.stocks_data['nse']
        
        for st in nse_stocks:
            for ind in indicators.keys():
                x = ind()
                x.data_fetcher = self.fetch_data_for_single
                res = x.get_indicator_values(st,start_date, end_date)
                row = today_data.index[today_data['Stock']==st]
                print('======',indicators[ind],'\n',row, res,'====')
                for col in res.columns[1:]:
                        today_data.at[row,col] = res[col].values[0]

        print(today_data)     
        today_data.to_csv('data_today.csv',mode='w', index=False)
        # print(stock_data)
    def append(self):
        '''
        Insert the data collected today to the database.

        Returns
        -------
        None.

        '''
        today_data = pd.read_csv('data_today.csv')
        self.db.insert_stock_data(today_data)
        print('Data collected today:\n ',today_data)


x = DataFetcher()
x.fetch()
x.calculate()
x.append()
