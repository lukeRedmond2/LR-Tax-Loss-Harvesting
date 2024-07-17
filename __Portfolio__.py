# Importing necessary libraries
from __Allocator__ import Allocator
from __Screener__ import Screener
from __DataLoader__ import DataLoader
from __Calculator__ import Calculator
from __Checker__ import Checker
from __Taxer__ import Taxer
from __OrderManager__ import OrderManager
from __Rebalancer__ import Rebalancer
from __TaxLossHarvester__ import TaxLossHarvester
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Portfolio class
class Portfolio():
    
	# Initialiser, adds stocks
    def __init__(self, universe, capital, size):
        
		# Setting portfolio attributes
        self.carry = 0
        self.size = size
        self.capital = capital
        self.starting_capital = capital
        self.universe = universe.copy()
        self.available_universe = universe.copy()
        
		# Setting manager dataframes for tracking trades and assets
        self.trades = pd.DataFrame({"Date":["filler"], "Symbol":["filler"], "Price":["filler"], "Quantity":["filler"], "Action":["filler"]})
        self.assets = pd.DataFrame({"Symbol":["filler"], "Quantity":["filler"]})

		# Setting the tools of the portfolio
        self.taxer = Taxer()
        self.checker = Checker()
        self.calculator = Calculator()
        self.loader = DataLoader()
        self.screener = Screener()
        self.allocator = Allocator()
        self.manager = OrderManager(self.loader)
        self.engine = TaxLossHarvester(self.checker, self.calculator, self.taxer, self.loader)
        self.rebalancer = Rebalancer(self.universe, self.capital, self.size, self.loader, self.screener, self.allocator)

		# Getting the quantities of stocks to initialise the portfolio
        allocated = self.rebalancer.RebalanceInit()
        
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
    
	# Method to run the TLH engine
    def Harvester(self, threshold):
		
        # Setting a copy of the assets
        temp_assets = self.assets.copy()
        harvests = []

		# Looping over all assets to assess quality of harvest
        for i in range(len(temp_assets)):
            
			# Extracting the individual asset and information
            current_asset = self.assets.iloc[i]["Symbol"]
            current_quantity = self.assets.iloc[i]["Quantity"]
            current_trades = self.trades.loc[self.trades["Symbol"] == current_asset]
            
            # Passing the filler value
            if current_asset != "filler":

			    # Checking if a harvest is allowed and good
                status, self.carry = self.engine.Harvest(current_trades, threshold, self.carry, True)
                print()
                print(f"Asset: {current_asset}, Harvest: {status}")
                if status == True:
					
				    # Harvesting
                    self.SellAsset(current_asset, current_quantity)
                    harvests.append(current_asset)
                
        # Getting the quantities to trade for the rebalance
        allocated = self.rebalancer.RebalanceTLH(harvests, temp_assets)
        
		# Looping over the allocated and checking if we need to buy or sell
        for index in range(len(allocated)):
            
			# Checking for a buy
            if allocated["Quantities"].iloc[index] > 0:
                
				# Buying the given quantity of given asset
                self.BuyAsset(allocated["Symbols"].iloc[index], allocated["Quantities"].iloc[index])
                
			# Checking for a sell
            elif allocated["Quantities"].iloc[index] < 0:
                
				# Selling the given quantity of given asset
                self.SellAsset(allocated["Symbols"].iloc[index], allocated["Quantities"].iloc[index])
                
			# Otherwise the quantity is 0
            else:
                pass
            
	# Method to rebalance the portfolio
    def Rebalance(self):
        
		# Getting the quantities to trade for the rebalance
        allocated = self.rebalancer.RebalanceReg(self.assets)
        
		# Looping over the allocated and checking if we need to buy or sell
        for index in range(len(allocated)):
            
			# Checking for a buy
            if allocated["Quantities"].iloc[index] > 0:
                
				# Buying the given quantity of given asset
                self.BuyAsset(allocated["Symbols"].iloc[index], allocated["Quantities"].iloc[index])
                
			# Checking for a sell
            elif allocated["Quantities"].iloc[index] < 0:
                
				# Selling the given quantity of given asset
                self.SellAsset(allocated["Symbols"].iloc[index], allocated["Quantities"].iloc[index])
                
			# Otherwise the quantity is 0
            else:
                pass