# Importing the necessary libraries
import pandas as pd
import numpy as np

# Class for rebalancing
class Rebalancer():
    
	# Initialiser
    def __init__(self, universe, capital, size, loader, screener, allocator):
        
		# Initialising the tools
        self.loader = loader
        self.screener = screener
        self.allocator = allocator
        
		# Setting portfolio attributes
        self.universe = universe.copy()
        self.capital = capital
        self.size = size
    
	# Method for initialising the portfolio's stocks
    def RebalanceInit(self):

		# Calculating the quantities for given stocks
        stocks = self.loader.Past(self.universe)
        screened = self.screener.Screen(stocks, self.size)
        allocated = self.allocator.Allocate(screened, self.capital, self.loader)
        specifics = allocated[["Symbols", "Quantities"]].copy()
        print("Goal quantities:")
        print(allocated)
        print()
        
		# Returning the allocated dataframe which contains quantities
        return specifics

	# Method for rebalancing based on TLH engine
    def RebalanceTLH(self, harvested, assets):
        
		# Setting the available universe to everything bar the harvested
        available = [asset for asset in self.universe if asset not in harvested]
        available_assets = assets.loc[[True if asset not in harvested else False for asset in assets["Symbol"].values]]
		
	    # Calculating the quantities for available
        stocks = self.loader.Past(available)
        screened = self.screener.Screen(stocks, self.size)
        allocated = self.allocator.Allocate(screened, self.capital, self.loader)
        specifics = allocated[["Symbols", "Quantities"]].copy()
        print("Goal quantities:")
        print(allocated)
        print()

        # Finding the stocks in assets that aren't in allocated
        for i in range(len(available_assets)):

			# Extracting the specifics of assets
            symbol = available_assets.iloc[i]["Symbol"]
            quantity = available_assets.iloc[i]["Quantity"]
            
		 	# Checking if it's not in allocated
            if symbol not in specifics["Symbols"].values:
                
		 	    # Updating the lists
                specifics.loc[len(specifics)+1] = [symbol, -quantity]
                    
			# Otherwise pass
            else:
                pass

		# Looping over the allocated
        for i in range(len(allocated)):
            
		 	# Extracting specifics
            symbol = allocated.iloc[i]["Symbols"]
            quantity = allocated.iloc[i]["Quantities"]
            
		 	# Checking if this asset is in the portfolio
            if symbol in assets["Symbol"].values:
                
                # Calculating the difference between the quantities
                difference = quantity - assets.loc[assets["Symbol"] == symbol]["Quantity"]
                specifics.loc[specifics["Symbols"]==symbol, "Quantities"] = difference.iloc[0]
        
        # Returning the allocated dataframe which contains quantities
        print("Necessary quantities:")
        print(specifics)
        print()
        return specifics
    
	# Method for a regular rebalance
    def RebalanceReg(self, assets):
        
		# Calculating the quantities for given stocks
        stocks = self.loader.Past(self.universe)
        screened = self.screener.Screen(stocks, self.size)
        allocated = self.allocator.Allocate(screened, self.capital, self.loader)
        specifics = allocated[["Symbols", "Quantities"]].copy()
        print("Goal quantities:")
        print(allocated)
        print()
            
		# Finding the stocks in assets that aren't in allocated
        for i in range(len(assets)):
            
            # Passing the filler value
            if assets.iloc[i]["Symbol"] != "filler":

			    # Extracting the specifics of assets
                symbol = assets.iloc[i]["Symbol"]
                quantity = assets.iloc[i]["Quantity"]

		 	    # Checking if it's not in allocated
                if symbol not in specifics["Symbols"].values:
                
		 		    # Updating the lists
                    specifics.loc[len(specifics)+1] = [symbol, -quantity]
                    
			# Otherwise pass
            else:
                pass
        
		# Finding the stocks in allocated that are in assets aready
        for i in range(len(allocated)):
            
		  	# Extracting the specifics of allocated
            symbol = allocated.iloc[i]["Symbols"]
            quantity = allocated.iloc[i]["Quantities"]
            
            # Checking if it's in assets
            if symbol in assets["Symbol"].values:
               
                # Calculating the difference in quantity between the two
                difference = quantity - assets.loc[assets["Symbol"] == symbol]["Quantity"]
                specifics.loc[specifics["Symbols"]==symbol, "Quantities"] = difference.iloc[0]
                
        # Returning the quantities to be traded
        print("Necessary quantities:")
        print(specifics)
        print()
        return specifics