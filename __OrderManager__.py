# Importing necessary libraries
from __DataLoader__ import DataLoader
from datetime import datetime
import pandas as pd

# Order manager class
class OrderManger():
    
	# Initialiser
    def __init__(self):
        pass
    
	# Method to create an order
    def MakeOrder(self, symbol, quantity, side):
        
		# Creating a data loader and extracting the live price
        dataloader = DataLoader()
        price = dataloader.Live(symbol, "price")
        
		# Getting today's date and time
        date = datetime.today()
        
		# Creating an order bracket
        bracket = pd.DataFrame({"Date":[date],
                                "Symbol":[symbol],
                                "Price":[price],
                                "Quantity":[quantity],
                                "Action":[side]})
        
		# Returning an order dataframe for the user
        return bracket