# Data sourcing, processing and visualization for Indian NSE Stock data.

In this project, I aim to perform data handling ( sourcing, cleaning, engineering and visualization) for a few of the NSE stock data. The stocks and their required symbol information are stored in a config file. I will automate code to fetch required stock data from investpy API and also add more features(RSI, Beta etc) that can help get more information. Using the built dataset, we will also make visualizations for understanding the data.

This project is divided into the following parts:
1.	Database setup
2.	Setting up a datastream.

## Database setup

For this project, I set up a NoSQL database - MongoDB. The main reason is the ease of setting it up and testing my flow quickly. It also data structuresfewer transformations.
For setting up the database, I installed MongoDB locally and the pymongo library in my python environment. Using MongoDB Compass which is a GUI for the database, I created the 'NiftyFifty' database. In that, I have initiallized 2 collections - 'last-update' and 'stock-data'. 'last-update' will be used to keep track of the last time data was added to the database, which helps in automating the data collection. 'stock-data' collection will be used to keep the actual dataset. 
The code to perform database operations is kept in the path database/database.py. It has functions to insert multiple stock data records. It also has a function to get the last-update of the database. In this project we mainly use the database for insertion and reading. No updates are performed.


##	Setting up a datastream.

Daily data collector is set up which can be run every day to get closing data since last insert in the database. Data_today.csv is a temporary file that is used to share data across the fetch, calculate and append functions of the stream for the data that is to be appended since the last-update. 
So far, RSI (Relative strength Index) and Beta (Volatility indicator) are calculated on the fetched stock closing prices. They are stored in the features folder at the root. 

The process of collecting data is as follows:
1.	For all the stocks listed in the config.csv, get historical data since the last insertion date. Store it in data_today.csv
2.	Use the data in the data_today.csv, calculate the engineered features like RSI, Beta and append it to the same file.
3.	Append the data in data_today.csv

# Some note:
- The features classes have a few common things – get_indicator_values function which returns the calculated values for a stock in the given date range. They also have a data_fetcher which is assigned to them by the daily data collector so that they only need to do calculations and not data fetching.
-	I have fetched 1 year data to have a good size for visualization, however we can run this script daily to get latest data.
