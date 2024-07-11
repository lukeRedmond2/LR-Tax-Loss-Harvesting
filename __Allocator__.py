# Importing necessaey libraries
import pandas as pd
import numpy as np

# Allocator class
class Allocator():
    
	# Initialiser
    def __init__(self):
        pass
    
	# Method to allocate capital to stcoks according to Mcap weighting
    def Allocate(self, screened, capital, loader):
        
        # Creating lists for storage of prices and caps
        prices = []
        caps = []

		# Looping over the keys to extract prices for each
        for index in range(len(screened)):
            
			# Updating the lists
            prices.append(loader.Live(screened.keys()[index], "price"))
            caps.append(loader.Live(screened.keys()[index], "mcap"))

        # Converting the lists to arrays
        prices = np.array(prices)
        caps = np.array(caps)

		# Calculations for the respective quantities
        totalcap = sum(caps)
        proportions = caps / totalcap
        allocations = proportions * capital
        quantities = allocations // prices

		# Sorting everything into a dataframe
        details = pd.DataFrame({"Symbols":screened.keys(),
                                "Market Cap":caps,
                                "Proportions":proportions,
                                "Allocations":allocations,
                                "Quantities":quantities,
                                "Prices":prices})
        
		# Returning this dataframe to the user
        return details