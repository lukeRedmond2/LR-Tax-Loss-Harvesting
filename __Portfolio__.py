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
import pickle

# Portfolio class
class Portfolio():
    
	# Initialiser, adds stocks
    def __init__(self, universe, capital, size, file=None):
        
        # If no file is provided, run regular initialisation protocol
        if file == None:

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
                
		# Otherwise attempt to load provided file data
        else:
            
			# Retrieving function
            self.LoadPortfolio(file)
            
			# Setting the tools of the portfolio
            self.taxer = Taxer()
            self.checker = Checker()
            self.calculator = Calculator()
            self.loader = DataLoader()
            self.screener = Screener()
            self.allocator = Allocator()
            self.manager = OrderManager(self.loader)
            self.engine = TaxLossHarvester(self.checker, self.calculator, self.taxer, self.loader)
            self.rebalancer = Rebalancer(self.universe, self.starting_capital, self.size, self.loader, self.screener, self.allocator)
        
	# Method to buy an asset for the portfolio
    def BuyAsset(self, symbol, quantity):
        
		# Creating the order
        order = self.manager.MakeOrder(symbol, quantity, "buy")
        
		# If the asset isn't already present on the portfolio
        if order["Symbol"][0] not in self.assets["Symbol"].values:
            
			# Checking if a new stock breaches the portfolio size
            if (len(self.assets)-1) >= self.size:
                print("Portfolio size limit reached. Cannot add new asset")
                print(f"Symbol: {order['Symbol'][0]}, Quantity: {order['Quantity'][0]}")
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
        self.capital -= float((order["Quantity"] * order["Price"]).iloc[0])
    
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
                print(f"Symbol: {order['Symbol'][0]}, Quantity: {order['Quantity'][0]}")
            
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
                self.capital += float((order["Quantity"] * order["Price"]).iloc[0])
            
		# Otherwise the position isn't present and shorting isn't allowed so...
        else:
            
			# Informing the user
            print("This position is not present and shorting isn't available")
            print(f"Symbol: {order['Symbol'][0]}, Quantity: {order['Quantity'][0]}")
    
	# Method to run the TLH engine
    def Harvester(self, threshold, taxinfo):
		
        # Setting a copy of the assets
        temp_assets = self.assets.copy()
        harvests = []
        
		# Looping over all assets to assess quality of harvest
        for i in range(len(temp_assets)):
            
			# Extracting the individual asset and information
            current_asset = temp_assets.iloc[i]["Symbol"]
            current_quantity = temp_assets.iloc[i]["Quantity"]
            current_trades = self.trades.loc[self.trades["Symbol"] == current_asset]
            
            # Passing the filler value
            if current_asset != "filler":

			    # Checking if a harvest is allowed and good
                status, self.carry, savings, taxes = self.engine.Harvest(current_trades, threshold, self.carry, taxinfo)
                print(f"Asset:                {current_asset:<16} Harvest:               {status}")
                print(f"Savings:              %{savings:<15} Carry forward losses:  ${self.carry:<15.2f}")
                print(f"Long term tax before: ${taxes[0]:<15.2f} Short term tax before: ${taxes[1]:<15.2f}")
                print(f"Long term tax after:  ${taxes[2]:<15.2f} Short term tax after:  ${taxes[3]:<15.2f}")
                print()
                if status == True:
					
				    # Harvesting
                    self.SellAsset(current_asset, current_quantity)
                    harvests.append(current_asset)

        # Getting the quantities to trade for the rebalance
        allocated = self.rebalancer.RebalanceTLH(harvests, temp_assets)
        
		# Sorting allocations by quant ascending to avoid full portfolio issue
        allocated = allocated.sort_values(by="Quantities").reset_index(drop=True)
        
		# Looping over the allocated and checking if we need to buy or sell
        for index in range(len(allocated)):
            
			# Checking for a buy
            if allocated["Quantities"].iloc[index] > 0:
                
				# Buying the given quantity of given asset
                self.BuyAsset(allocated["Symbols"].iloc[index], allocated["Quantities"].iloc[index])
                
			# Checking for a sell
            elif allocated["Quantities"].iloc[index] < 0:
               
				# Selling the given quantity of given asset
                self.SellAsset(allocated["Symbols"].iloc[index], abs(allocated["Quantities"].iloc[index]))
                
			# Otherwise the quantity is 0
            else:
                pass
            
	# Method to rebalance the portfolio
    def Rebalance(self):
        
		# Getting the quantities to trade for the rebalance
        allocated = self.rebalancer.RebalanceReg(self.assets)
        
		# Sorting allocations by quant ascending to avoid full portfolio issue
        allocated = allocated.sort_values(by="Quantities").reset_index(drop=True)

		# Looping over the allocated and checking if we need to buy or sell
        for index in range(len(allocated)):
            
			# Checking for a buy
            if allocated["Quantities"].iloc[index] > 0:
                
				# Buying the given quantity of given asset
                self.BuyAsset(allocated["Symbols"].iloc[index], allocated["Quantities"].iloc[index])
                
			# Checking for a sell
            elif allocated["Quantities"].iloc[index] < 0:
                
				# Selling the given quantity of given asset
                self.SellAsset(allocated["Symbols"].iloc[index], abs(allocated["Quantities"].iloc[index]))
                
			# Otherwise the quantity is 0
            else:
                pass
            
    # Method to calculate gains
    def CurrentGains(self):
        
        # Storage of gains
        total_realised = 0
        total_unrealised = 0
        
		# Isolating every asset to ever be traded on the portfolio
        assets_w_dups = []
        
		# Looping over the trades
        for i in range(len(self.trades)):
            
            # Passing the filler value
            if self.trades.iloc[i]["Symbol"] != "filler":
                
                # Updating the list
                assets_w_dups.append(self.trades.iloc[i]["Symbol"])
                
		    # Passing otherwise
            else:
                pass
            
		# Removing duplicates by creating a set
        assets = set(assets_w_dups)
        assets = list(assets) 

		# Looping over the every asset ever
        for i in range(len(assets)):
                
			# Calculating the individual gains and updating the totals
            gains = self.calculator.Calculate(self.trades.loc[self.trades["Symbol"]==assets[i]], self.loader.Live(assets[i], "price"))
            total_realised += (gains[0] + gains[1])
            total_unrealised += (gains[2] + gains[3])

		# Informing the user and returning the gains
        print(f"Total Realised Gains:   {round(total_realised, 2)}")
        print(f"Total Unrealised Gains: {round(total_unrealised, 2)}")
        return total_realised, total_unrealised

	# Method to save current portfolio data
    def SavePortfolio(self, filename):
        
        # Extracting the attributes
        data = {"carry":self.carry,
                "size":self.size,
                "capital":self.capital,
                "starting_capital":self.starting_capital,
                "universe":self.universe,
                "available_universe":self.available_universe,
                "trades":self.trades,
                "assets":self.assets}

		# Context manager
        with open(filename, "wb") as f:
            pickle.dump(data, f)
            
	# Method for loading previous portfolio data
    def LoadPortfolio(self, filename):
        
		# Attempting to retrieve data
        try:
            
			# Context manager
            with open(filename, "rb") as f:
                
				# Loading the data and pasting it to the portfolio
                data = pickle.load(f)
                self.carry = data["carry"]
                self.size = data["size"]
                self.capital = data["capital"]
                self.starting_capital = data["starting_capital"]
                self.universe = data["universe"]
                self.available_universe = data["available_universe"]
                self.trades = data["trades"]
                self.assets = data["assets"]
        
		# Handling a file not found error
        except FileNotFoundError:
            print("Save file not found.")