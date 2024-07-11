# Importing necessary libraries
from datetime import datetime, timedelta

# Stock screener class
class Screener():
    
	# Initialiser
    def __init__(self):
        pass
        
	# Method to actually screen the stocks
    def Screen(self, data, count):
        
		# Getting the bounds
        before=data.loc[datetime.today()-timedelta(30):datetime.today()].iloc[0]
        after=data.loc[datetime.today()-timedelta(30):datetime.today()].iloc[-1]
        
		# Calculating the monthly returns
        returns = (((after-before) / before) * 100).sort_values(ascending=False)
        
		# Filtering out the best performing
        return returns.iloc[:count]