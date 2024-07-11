# Importing necessary libraries
from __DataLoader__ import DataLoader
from __Screener__ import Screener
from __Allocator__ import Allocator
from __OrderManager__ import OrderManger
from __Rebalancer__ import Rebalance
from datetime import datetime
import pandas as pd

# Portfolio class
class Portfolio():
    
	# Initialiser
    def __init__(self, universe, capital, size):
        
		# Setting portfolio attributes
        self.size = size
        self.capital = capital
        self.universe = universe.copy()
        self.available_universe = universe.copy()
        
		# Setting manager dataframes for tracking trades and assets
        self.trades = pd.DataFrame({"Date":["filler", datetime(2021,1,1), datetime(2022,3,4), datetime(2023,1,1), datetime(2023,2,2)],
                                    "Symbol":["filler", "SOFI", "SOFI", "AAPL", "AAPL"],
                                    "Price":["filler", 200, 250, 200, 240],
                                    "Quantity":["filler", 10, 10, 10, 10],
                                    "Action":["filler", "buy", "sell", "buy", "sell"]})
        self.assets = pd.DataFrame({"Symbol":["filler"], "Quantity":["filler"], "LT Gains":["filler"], "ST Gains":["filler"]})
        self.manager = OrderManger()

		# Objects for choosing the top stocks of our universe
        loader = DataLoader()
        screener = Screener()
        allocator = Allocator()
        
		# Calculating quantities for what stocks
        stocks = loader.Past(self.universe)
        screened = screener.Screen(stocks, self.size)
        allocated = allocator.Allocate(screened, self.capital, loader)
        
		# Looping over the chosen stocks and adding them to the portfolio
        for index in range(len(allocated)):
            
			# Adding the asset
            self.BuyAsset(allocated["Symbols"].iloc[index], allocated["Quantities"].iloc[index])
        
	# Method to buy an asset for the portfolio
    def BuyAsset(self, symbol, quantity):
        
		# Creating the order
        order = self.manager.MakeOrder(symbol, quantity, "buy")
        
		# If the asset isn't already present on the portfolio
        if order["Symbol"][0] not in self.assets["Symbol"].values:
            
			# Checking if a new stock breaches the portfolio size
            if (len(self.assets)-1) >= self.size:
                print("Portfolio size limit reached. Cannot add new asset")
                return
            
			# Adding the asset to the portfolio asset list
            update = pd.DataFrame({"Symbol":[order["Symbol"][0]], "Quantity":[order["Quantity"].values[0]]})
            self.assets = pd.concat([self.assets, update]).reset_index(drop=True)
            
			# Logging the trade
            self.trades = pd.concat([self.trades, order]).reset_index(drop=True)
            
			# Updating the list of available stocks that aren't under the portfolio
            self.available_universe.remove(order["Symbol"][0])
        
		# Otherwise if the asset is already in the portfolio
        else:
            
			# Updating the quantity of the assets
            current_quantity = self.assets.loc[self.assets["Symbol"]==order["Symbol"][0], "Quantity"].values[0]
            new_quantity = current_quantity + order["Quantity"].values[0]
            self.assets.loc[self.assets["Symbol"]==order["Symbol"][0], "Quantity"] = new_quantity
            
			# Logging the other trades
            self.trades = pd.concat([self.trades, order]).reset_index(drop=True)

		# Updating the capital
        self.capital -= (order["Quantity"] * order["Price"])
    
	# Method to sell an asset for the portfolio
    def SellAsset(self, symbol, quantity):
        
        # Creating the order
        order = self.manager.MakeOrder(symbol, quantity, "sell")

		# If the asset is already present on the portfolio
        if order["Symbol"][0] in self.assets["Symbol"].values:
            
			# Calculating the new portfolio quantity of the asset
            current_quantity = self.assets.loc[self.assets["Symbol"]==order["Symbol"][0], "Quantity"].values[0]
            new_quantity = current_quantity - order["Quantity"].values[0]
            
			# Checking if the sale quantity was greater than current quantity (Short sale)
            if new_quantity < 0:
                
				# Inform the user and exit
                print("Quantity too great, no short sales allowed")
            
			# If the sale cancels out position completely then remove it from assets
            elif new_quantity == 0:
                
				# Removing the asset from the portfolio
                self.assets = self.assets.loc[self.assets["Symbol"] != order["Symbol"][0]].reset_index(drop=True)
                
				# Logging the trade
                self.trades = pd.concat([self.trades, order]).reset_index(drop=True)
                
				# Updating the capital
                self.capital += (order["Quantity"] * order["Price"])
                
				# Updating the stocks that we don't have under the portfolio
                self.available_universe.append(order["Symbol"][0])
            
			# Otherwise if there would still be a remaining amount
            else:
                
				# Updating the asset's quantity on the portfolio
                self.assets.loc[self.assets["Symbol"]==order["Symbol"][0], "Quantity"] = new_quantity
                
				# Combining with the other trades
                self.trades = pd.concat([self.trades, order]).reset_index(drop=True)
                
				# Updating the capital
                self.capital += (order["Quantity"] * order["Price"])
            
		# Otherwise the position isn't present and shorting isn't allowed so...
        else:
            
			# Informing the user
            print("This position is not present and shorting isn't available")
            
	# Method for rebalancing the portfolio
    def Rebalance(self):
        
		# Defining a rebalancer
        rebalancer = Rebalance()
        
		# Running the TLH engine of the rebalancer
        harvest = rebalancer.Engine(self.trades, self.assets)
        
		# Objects for choosing the top stocks of our universe
        loader = DataLoader()
        screener = Screener()
        allocator = Allocator()
        
        print()
        print(self.universe)
        print(self.available_universe)

        # Only harvest if there's stuff to harvest
        if harvest != None:
            
		    # Harvesting
            for i in range(len(harvest)):
            
			    # Extracting the quantity
                quantity = self.assets[self.assets["Symbol"]==harvest.iloc[i]]["Quantity"].item()
            
			    # Harvesting the position
                self.SellAsset(harvest.iloc[i], quantity)
            
        print()
        print(self.universe)
        print(self.available_universe)
        print()
        
		# Calculating quantities for what stocks
        stocks = loader.Past(self.universe)
        screened = screener.Screen(stocks, self.size)
        allocated = allocator.Allocate(screened, self.capital, loader)
        print(allocated)