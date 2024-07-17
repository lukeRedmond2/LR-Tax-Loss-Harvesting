# Importing necessary libraries
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Calculating realised, unrealised, long and short term gains or losses
class Calculator():
    
	# Initialiser
    def __init__(self):
        pass
    
	# Method for calculating the gains or losses
    def Calculate(self, trades, current):
        
		# Calculating realised and unrealised, short and long term gains
        def CalculateGains(trades, current_price):
    
            # Initialise different gains storage
            realised_long_term_gains = 0
            realised_short_term_gains = 0
            unrealised_long_term_gains = 0
            unrealised_short_term_gains = 0

            # These lists contain their respective long positions
            all_long_positions = []
            short_term_long_positions = []
            long_term_long_positions = []

            # Looping over all trades
            for i in range(len(trades)):
    
                # Extracting a row for easier indexing
                row = trades.iloc[i]
    
                # Checking if it's a buy
                if row["Action"] == "buy":
    
                    # Appending all buys no matter the term
                    all_long_positions.append(row.copy())
    
                # Checking if it's a sell
                elif row["Action"] == "sell":
    
                    # Gathering specific sell details
                    og_shares_sold = row["Quantity"]
                    shares_sold = row["Quantity"]
                    price_sold = row["Price"]
                    date_sold = row["Date"]
                    total_short_term_cost_basis = 0
                    total_long_term_cost_basis = 0

                    # Reset positions lists
                    short_term_long_positions = []
                    long_term_long_positions = []

                    # Checking for long term or short term buys
                    for pos in all_long_positions:
    
                        # If the purchase was made more than a year before the sale
                        if pos["Date"] < (date_sold - timedelta(365)):
    
                            # Adding to the long term list
                            long_term_long_positions.append(pos)

                        # Otherwise                
                        else:
    
                            # Adding to the short term list
                            short_term_long_positions.append(pos)

                    # Process the shares sold for long term
                    while shares_sold > 0 and long_term_long_positions:
    
                        # Extracting the oldest long term buy
                        oldest_long_term_buy = long_term_long_positions[0]
    
                        # Checking if there are more shares sold than the quantity of the oldest buy
                        if shares_sold >= oldest_long_term_buy["Quantity"]:
    
                            # Calculating the cost basis
                            total_long_term_cost_basis += (oldest_long_term_buy["Quantity"] * oldest_long_term_buy["Price"])
    
                            # Updating the amount of shares left to handle
                            shares_sold -= oldest_long_term_buy["Quantity"]
    
                            # All oldest shares were used so they can be discarded
                            all_long_positions.remove(oldest_long_term_buy)
                            long_term_long_positions.pop(0)
    
                        # Otherwise deal with remaining shares
                        else:
    
                            # Calculating the basis as the remaining shares to sell times oldest price
                            total_long_term_cost_basis += (shares_sold * oldest_long_term_buy["Price"])
    
                            # Updating the amount of shares left on the oldest buy
                            oldest_long_term_buy["Quantity"] -= shares_sold

                            # No shares left to sell so setting it to zero which exits the loop
                            shares_sold = 0

                    # Total long term proceeds - the accurate cost basis
                    long_term_sold = og_shares_sold - shares_sold
                    long_term_proceeds = long_term_sold * price_sold
                    realised_long_term_gains += long_term_proceeds - total_long_term_cost_basis
    
                    # Reset shares sold for short-term calculation
                    shares_sold = og_shares_sold - long_term_sold

                    # Process the shares sold for short term
                    while shares_sold > 0 and short_term_long_positions:
    
                        # Extracting the oldest short term buy
                        oldest_short_term_buy = short_term_long_positions[0]
    
                        # Checking if there are more shares sold than the quantity of the oldest buy
                        if shares_sold >= oldest_short_term_buy["Quantity"]:
    
                            # Calculating the cost basis
                            total_short_term_cost_basis += (oldest_short_term_buy["Quantity"] * oldest_short_term_buy["Price"])
    
                            # Updating the amount of shares left to handle
                            shares_sold -= oldest_short_term_buy["Quantity"]
    
                            # All oldest shares were used so they can be discarded
                            all_long_positions.remove(oldest_short_term_buy)
                            short_term_long_positions.pop(0)
    
                        # Otherwise deal with remaining shares
                        else:
    
                            # Calculating the basis as the remaining shares to sell times oldest price
                            total_short_term_cost_basis += (shares_sold * oldest_short_term_buy["Price"])
    
                            # Updating the amount of shares left on the oldest buy
                            oldest_short_term_buy["Quantity"] -= shares_sold

                            # No shares left to sell so setting it to zero which exits the loop
                            shares_sold = 0

                    # Total short term proceeds - the accurate cost basis
                    short_term_sold = og_shares_sold - long_term_sold
                    short_term_proceeds = short_term_sold * price_sold
                    realised_short_term_gains += short_term_proceeds - total_short_term_cost_basis
            
            # Looping over the
            for position in all_long_positions:
        
		        # Calculating the current value of these positions
                current_value = position["Quantity"] * current_price
        
		        # Checking if the position is long or short term
                if position["Date"] < (datetime.today()-timedelta(365)):
            
			        # Updating the unrealised long term gains
                    unrealised_long_term_gains += current_value - (position["Quantity"] * position["Price"])
            
		        # Otherwise it's short term
                else:
            
			        # Updating the unrealised short term gains
                    unrealised_short_term_gains += current_value - (position["Quantity"] * position["Price"])
            
            # Returning the all the individual gains    
            return round(realised_long_term_gains, 2), round(realised_short_term_gains, 2), round(unrealised_long_term_gains, 2), round(unrealised_short_term_gains, 2)
		
		# Extracting the tuple of all gains
        all_gains = CalculateGains(trades, current)
        
		# Returning the gains to the user
        return all_gains       