# financial_data
Data sourcing and visualization for Indian Nifty 50 stock data

1. Setting up database and code to access it.
2. Set up data collector to fetch and insert data from investpy.



## Setting up database and code to access it

For this project, I set up a NoSQL database - MongoDB. The main reason is the ease of setting it up and testing my flow quickly as well as the data structures requiring fewer transformations.

For setting up the database, I installed MongoDB locally and the pymongo library in my python environment. Using MongoDB Compass which is a GUI for the database, I created the 'NiftyFifty' database. In that, I have initiallized 2 collections - 'last-update' and 'stock-data'. 'last-update' will be used to keep track of the last time data was added to the database, which helps in automating the data collection. 'stock-data' collection will be used to keep the actually dataset. As an initial step, only the closing price has been added. A data point conists of the fields *date*, *stock* and *close*. Later financial calculations like RSI, Beta etc will be added.
