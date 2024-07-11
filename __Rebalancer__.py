# Importing the necessary libraries
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Rebalancing the portfolio
class Rebalance():
    
	# Initialiser
    def __init__(self):
        pass
    
	# Method for running the TLH engine
    def Engine(self, trades, assets):
        
        # Calculate short and long term gains for each of those symbol
        def CalculateGains(trades, assets):
            
			# These lists and variables store gains data
            total_long_term_gains = 0
            total_short_term_gains = 0
            individual_long_term_gains = []
            individual_short_term_gains = []
    
            # Looping over the assets
            for i in range(len(assets)):

                # Passing the filler value
                if assets.iloc[i]["Symbol"] != "filler":

				    # Extracting the symbol and its respective trades
                    current_symbol = assets.iloc[i]["Symbol"]
                    current_trades = trades[trades["Symbol"] == current_symbol]
                    
					# Initialise different gains storage
                    short_term_gains = 0
                    long_term_gains = 0
    
                    # These lists contain their respective long positions
                    all_long_positions = []
                    short_term_long_positions = []
                    long_term_long_positions = []

	    			# Looping over all trades
                    for i in range(len(current_trades)):
	    		
	    				# Extracting a row for easier indexing
                        row = current_trades.iloc[i]
	    		
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

	    					# Checking for long term or short term buys
                            for j in range(len(all_long_positions)):
	    				
	                            # If the purchase was made more than a year before the sale
                                if all_long_positions[j]["Date"] < (date_sold - timedelta(365)):
	    					
	    	                        # Adding to the long term list
                                    long_term_long_positions.append(j)

	    						# Otherwise                
                                else:
	    					
	    							# Adding to the short term list
                                    short_term_long_positions.append(j)

	    					# Process the shares sold for long term
                            while shares_sold > 0 and long_term_long_positions:
	    			
	    						# Extracting the oldest long term buy
                                oldest_long_term_buy_index = long_term_long_positions[0]
                                oldest_long_term_buy = all_long_positions[oldest_long_term_buy_index]
	    				
	    						# Checking if there are more shares sold than the quantity of the oldest buy
                                if shares_sold >= oldest_long_term_buy["Quantity"]:
	    				
	    							# Calculating the cost basis
                                    total_long_term_cost_basis += (oldest_long_term_buy["Quantity"] * oldest_long_term_buy["Price"])
	    					
	    							# Updating the amount of shares left to handle
                                    shares_sold -= oldest_long_term_buy["Quantity"]
	    					
	    							# All oldest shares were used so they can be discarded
                                    long_term_long_positions.pop(0)
	    				
	    						# Otherwise deal with remaining shares
                                else:
	    					
	    							# Calculating the basis as the remaining shares to sell times oldest price
                                    total_long_term_cost_basis += (shares_sold * oldest_long_term_buy["Price"])
	    					
	    							# Updating the amount of shares left on the oldest buy
                                    all_long_positions[oldest_long_term_buy_index]["Quantity"] -= shares_sold

	    							# No shares left to sell so setting it to zero which exits the loop
                                    shares_sold = 0

	    					# Total long term proceeds - the accurate cost basis
                            long_term_sold = og_shares_sold - shares_sold
                            long_term_proceeds = long_term_sold * price_sold
                            long_term_gains += long_term_proceeds - total_long_term_cost_basis
	    			
                            # Reset shares sold for short-term calculation
                            shares_sold = og_shares_sold - long_term_sold

	    					# Process the shares sold for short term
                            while shares_sold > 0 and short_term_long_positions:
	    				
	    						# Extracting the oldest short term buy
                                oldest_short_term_buy_index = short_term_long_positions[0]
                                oldest_short_term_buy = all_long_positions[oldest_short_term_buy_index]
	    				
	    						# Checking if there are more shares sold than the quantity of the oldest buy
                                if shares_sold >= oldest_short_term_buy["Quantity"]:
	    					
	    							# Calculating the cost basis
                                    total_short_term_cost_basis += (oldest_short_term_buy["Quantity"] * oldest_short_term_buy["Price"])
	    					
	    							# Updating the amount of shares left to handle
                                    shares_sold -= oldest_short_term_buy["Quantity"]
	    					
	    							# All oldest shares were used so they can be discarded
                                    short_term_long_positions.pop(0)
	    				
	    						# Otherwise deal with remaining shares
                                else:
	    					
	    							# Calculating the basis as the remaining shares to sell times oldest price
                                    total_short_term_cost_basis += (shares_sold * oldest_short_term_buy["Price"])
	    					
	    							# Updating the amount of shares left on the oldest buy
                                    all_long_positions[oldest_short_term_buy_index]["Quantity"] -= shares_sold

	    							# No shares left to sell so setting it to zero which exits the loop
                                    shares_sold = 0

	    					# Total short term proceeds - the accurate cost basis
                            short_term_sold = og_shares_sold - long_term_sold
                            short_term_proceeds = short_term_sold * price_sold
                            short_term_gains += short_term_proceeds - total_short_term_cost_basis
                    
					# Excluding the losses as if they're unrealised
                    if long_term_gains > 0:
                        total_long_term_gains += long_term_gains
                    if short_term_gains > 0:
                        total_short_term_gains += short_term_gains
                    individual_long_term_gains.append(long_term_gains)
                    individual_short_term_gains.append(short_term_gains)
                    
				# Otherwise adding the filler value
                else:
                    
					# Appending the filler
                    individual_long_term_gains.append("filler")
                    individual_short_term_gains.append("filler")
                    
			# After the loop update the assets to include respective gains or losses
            assets["LT Gains"] = individual_long_term_gains
            assets["ST Gains"] = individual_short_term_gains
                    
            # Might change to flooring the decimal
            return round(total_long_term_gains, 2), round(total_short_term_gains, 2), assets

        # Filtering out the positions at losses
        def FindLosses(assets):
            
            # Boolean mask storage
            mask = []

            # Filter them out
            for i in range(len(assets)):
                
				# Passing the filler value
                if assets.iloc[i]["Symbol"] != "filler":
                    
					# Checking if the long term gains
                    if assets.iloc[i]["LT Gains"] < 0 or assets.iloc[i]["ST Gains"] < 0:
                        
						# Updating the mask
                        mask.append(True)
                        
					# Otherwise
                    else:
                        
						# Updating the mask
                        mask.append(False)
                        
				# Otherwise
                else:
                    
					# Updating the mask
                    mask.append(False)

			# Returning the mask to filter       
            return mask
                    
        # Filtering out violations of wash sale rule
        def WashSale(assets, trades):
            
			# Boolean mask storage
            mask = []
            
			# Looping over the already filtered assets
            for i in range(len(assets)):
                    
				# Extracting specifics
                current_symbol = assets.iloc[i]["Symbol"]
                current_trades = trades[trades["Symbol"] == current_symbol]
                
                # Doesn't violate yet
                is_safe = True
                    
				# Looping over the trades of a specific symbol
                for j in range(len(current_trades)):
                        
					# Checking if the trade falls in the wash sale period
                    if (datetime.today() - timedelta(30)) <= current_trades["Date"].iloc[j] <= (datetime.today() + timedelta(30)):
                            
						# Violation
                        is_safe = False
                        break
                    
				# Updating the mask with respective boolean
                mask.append(is_safe)
                    
			# Returning the mask
            return mask

        # Calculating tax due before and after
        def CalculateTax(assets, long_term_gains, short_term_gains):
            
			# Long term tax before
            if long_term_gains > 0:
                long_term_tax_before = 0.1 * long_term_gains
            else:
                long_term_tax_before = 0
                
			# Short term tax before
            if short_term_gains > 0:
                short_term_tax_before = 0.2 * short_term_gains
            else:
                short_term_tax_before = 0
                
			# Calculate the total tax before
            total_tax_before = long_term_tax_before + short_term_tax_before

			# Calculate total losses to offset the gains
            total_long_term_losses = assets["LT Gains"].sum()
            total_short_term_losses = assets["ST Gains"].sum()
            
            # Net gains after offsetting losses
            net_long_term_gains = total_long_term_gains + total_long_term_losses
            net_short_term_gains = total_short_term_gains + total_short_term_losses
            
			# Ensure that net gains cannot be negative
            net_long_term_gains = max(net_long_term_gains, 0)
            net_short_term_gains = max(net_short_term_gains, 0)

			# Long term tax after
            if net_long_term_gains > 0:
                long_term_tax_after = 0.1 * net_long_term_gains
            else:
                long_term_tax_after = 0
                
            # Short term tax after
            if net_short_term_gains > 0:
                short_term_tax_after = 0.2 * net_short_term_gains
            else:
                short_term_tax_after = 0
                
			# Calculating the total tax before and after the harvest
            total_tax_after = long_term_tax_after + short_term_tax_after
            print(f"Total tax before: ${total_tax_before}")
            print(f"Total tax after:  ${total_tax_after}")
            
			# Calculating the savings
            if total_tax_before - total_tax_after > 0:
                print(f"Savings after harvest: ${total_tax_before - total_tax_after}")
                return assets["Symbol"]

        # Calculating the gains and losses of each symbol and the totals
        total_long_term_gains, total_short_term_gains, assets = CalculateGains(trades, assets)
        print(f"LT Gains: ${total_long_term_gains}")
        print(f"ST Gains: ${total_short_term_gains}")
        print()
        print("All Assets:")
        print(assets)
        print()
        loss_mask = FindLosses(assets)
        assets_at_loss = assets[loss_mask]           
        print("Assets At Loss:")
        print(assets_at_loss)
        print()
        safe_mask = WashSale(assets_at_loss, trades)
        print("Safe Assets")
        print(assets_at_loss[safe_mask])
        print()
        if total_long_term_gains+total_short_term_gains > 0:
            if assets_at_loss[safe_mask].empty == False:
                harvest = CalculateTax(assets_at_loss[safe_mask], total_long_term_gains, total_short_term_gains)
                print()
                print(harvest)
                return harvest
            else:
                print("No losses to harvest")
                return None
        else:
            print("No gains to be taxed")
            return None