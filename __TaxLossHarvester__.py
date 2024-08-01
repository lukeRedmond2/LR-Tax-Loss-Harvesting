# Importing necessary libraries
import numpy as np

# Tax loss harvesting engine
class TaxLossHarvester():
    
	# Initialiser
    def __init__(self, checker, calculator, taxer, loader):
        
		# Setting the base functions for harvesting
        self.calculator = calculator
        self.checker = checker
        self.loader = loader
        self.taxer = taxer
    
	# Method for harvesting
    def Harvest(self, trades, threshold, carry, info):
        
		# Checking if the trades violate the wash sale
        status = self.checker.Check(trades)
        
		# Checking if the status is good
        if status == True:

            # Extracting the symbol and its price
            symbol = trades.iloc[0]["Symbol"]
            current = self.loader.Live(symbol, "price")

            # Extracting the realised and unrealised gains
            gains = self.calculator.Calculate(trades, current)
            
            # Calculating the taxes due
            savings, taxes, carry = self.taxer.Tax(gains, carry, info)

			# Checking conditions for the harvest
            if savings >= threshold:
                
				# It's good for harvesting
                return True, carry, savings, taxes

			# Otherwise no harvest
            else:

                # Not good for harvesting
                return False, carry, savings, taxes
            
		# Otherwise no harvest
        else:
            
			# Not good for harvesting
            return False, carry, 0, (0,0,0,0)