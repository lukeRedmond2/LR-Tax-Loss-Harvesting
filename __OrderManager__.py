# Importing necessary libraries
from datetime import datetime
import pandas as pd

# Order manager class
class OrderManager():
    
	# Initialiser
    def __init__(self, loader):
        
		# Setting the dataloader
        self.loader = loader
    
	# Method to create an order
    def MakeOrder(self, symbol, quantity, side):
        
		# Creating a data loader and extracting the live price
        price = self.loader.Live(symbol, "price")
        
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