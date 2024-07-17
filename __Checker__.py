# Importing necessary libraries
from datetime import datetime, timedelta

# Checking trades for wash sale
class Checker():
    
	# Initialiser
    def __init__(Self):
        pass
    
	# Method for checking
    def Check(self, trades):
        
		# Setting time variables
        today = datetime.today()
        delta = timedelta(30)
        
		# Looping over the trades
        for i in range(len(trades)):
            
			# Isolating the trade date
            date = trades.iloc[i]["Date"]
            
            # Setting the status
            safe = True

			# Check if it falls within the period
            if (today-delta) <= date <= (today+delta):
                
				# Updating the status and exiting the loop
                safe = False
                break
                
		# Checking if the final status is safe
        if safe:
            
			# Returning true if they don't violate washsale
            return True
        
		# Otherwise...
        else:
            
			# Returning false as they don't violate washsale
            return False