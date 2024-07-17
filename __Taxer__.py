# Importing the necessary libraries
import numpy as np

# Calculating the tax due before and after a harvest
class Taxer():
    
    # Initialiser
    def __init__(self):
        pass
    
    # Method for calculating
    def Tax(self, gains, carry_forward, print_info):
        
        # Extracting the specific gains and setting some initial values
        long_term_realised, short_term_realised, long_term_unrealised, short_term_unrealised = gains
        long_term_remaining = long_term_realised
        short_term_remaining = short_term_realised
        final_forward = carry_forward
        og = carry_forward
        
		# Checking if the user wants printouts
        if print_info == True:
            
		    # Informing user of their inputs
            print(f"LT Realised Gains:   {long_term_realised}")
            print(f"ST Realised Gains:   {short_term_realised}")
            print(f"LT Unrealised Gains: {long_term_unrealised}")
            print(f"ST Unrealised Gains: {short_term_unrealised}")
        
        # Calculate initial tax before considering unrealized losses
        long_term_tax_before = max(0, long_term_realised) * 0.1
        short_term_tax_before = max(0, short_term_realised) * 0.2
        
		# Checking if the user wants printouts
        if print_info == True:
            
		    # Informing user of the tax due before a harvest
            print(f"LT before: {long_term_tax_before}")
            print(f"ST before: {short_term_tax_before}")
        
		# Handling long term unrealized losses
        if long_term_unrealised < 0 and long_term_realised > 0:
            
			# If the losses don't cancel the gains and more
            if long_term_realised >= abs(long_term_unrealised):
                
				# Calculating the tax and other important variables
                long_term_tax_after = (long_term_realised + long_term_unrealised) * 0.1
                long_term_remaining_loss = 0
                long_term_remaining = (long_term_realised + long_term_unrealised)
                # print("1. LT if")
                
			# Otherwise the losses completely cancel the gains and can be used elsewhere
            else:
                
				# Setting tax after to 0 and finding other important variables
                long_term_tax_after = 0
                long_term_remaining_loss = long_term_realised + long_term_unrealised
                long_term_remaining = 0
                # print("1. LT else")
                
		# No unrealised losses
        else:
            
			# Checking if gains are positive
            if long_term_unrealised + long_term_realised >= 0:
                
				# Calculating the tax after and other important variables
                long_term_tax_after = (long_term_realised + long_term_unrealised) * 0.1
                long_term_remaining_loss = 0
                long_term_remaining = (long_term_realised + long_term_unrealised)
                # print("2. LT if")
                
			# Otherwise there are leftover losses
            else:
                
				# Setting tax after to 0 and finding other important variables
                long_term_tax_after = 0
                long_term_remaining_loss = (long_term_realised + long_term_unrealised)
                long_term_remaining = 0
                # print("2. LT else")
                
        # Handling short term unrealised losses
        if short_term_unrealised < 0 and short_term_realised > 0:
            
			# If the losses don't cancel the gains and more
            if short_term_realised >= abs(short_term_unrealised):
                
				# Calculating the tax and other important variables
                short_term_tax_after = (short_term_realised + short_term_unrealised) * 0.2
                short_term_remaining_loss = 0
                short_term_remaining = (short_term_realised + short_term_unrealised)
                # print("3. ST if")
                
			# Otherwise the losses completely cancel out the gains and can be used elsewhere
            else:
                
				# Setting tax after to 0 and finding other important variables
                short_term_tax_after = 0
                short_term_remaining_loss = short_term_realised + short_term_unrealised
                short_term_remaining = 0
                # print("3. ST else")
                
		# No unrealised losses
        else:
            
            # Checking if gains are positive
            if short_term_unrealised + short_term_realised >= 0:
                
				# Calculating the tax after and other important variables
                short_term_tax_after = (short_term_realised + short_term_unrealised) * 0.2
                short_term_remaining_loss = 0
                short_term_remaining = (short_term_realised + short_term_unrealised)
                # print("4. ST if")
                
			# Otherwise there are leftover losses
            else:
                
				# Setting tax after to 0 and finding other important variables
                short_term_tax_after = 0
                short_term_remaining_loss = (short_term_realised + short_term_unrealised)
                short_term_remaining = 0
                # print("4. ST else")
            
		# Handling any remaining long term losses
        if long_term_remaining_loss < 0:
            
            # If there are still short term gains to offset
            if short_term_remaining > 0:

				# If the losses don't cancel the gains and more
                if short_term_remaining >= abs(long_term_remaining_loss):
                    
					# Calculating the new tax and finding other important variables
                    short_term_tax_after = (short_term_remaining + long_term_remaining_loss) * 0.2
                    short_term_remaining = (short_term_remaining + long_term_remaining_loss)
                    long_term_remaining_loss = 0
                    # print("5. if")
                
				# Otherwise there are still leftover losses
                else:
                    
					# Setting the remaining tax to 0 and setting other variables
                    short_term_tax_after = 0
                    long_term_remaining_loss = short_term_remaining + long_term_remaining_loss
                    short_term_remaining = 0
                    # print("5. else")

			# There are no more gains to offset
            else:
                # print("5. no gains")
                pass
                
		# Handling any remaining short term losses
        if short_term_remaining_loss < 0:
            
			# If there are still long term gains to offset
            if long_term_remaining > 0:
                
				# If the losses don't cancel the gains and more
                if long_term_remaining >= abs(short_term_remaining_loss):
                                        
					# Calculating the new tax and finding other important variables
                    long_term_tax_after = (long_term_remaining + short_term_remaining_loss) * 0.1
                    long_term_remaining = (long_term_remaining + short_term_remaining_loss)
                    short_term_remaining_loss = 0
                    # print("6. if")
                    
				# Otherwise there are still leftover losses
                else:
                    
					# Setting the remaining tax to 0 and setting other variables
                    long_term_tax_after = 0
                    short_term_remaining_loss = long_term_remaining + short_term_remaining_loss
                    long_term_remaining = 0
                    # print("6. else")
                    
			# There are no more gains to offset
            else:
                # print("6. no gains")
                pass
        
		# Checking if there are any carry forward losses
        if carry_forward < 0:
            
			# Checking if any short term gains left (offset them first because of the higher rate)
            if short_term_remaining > 0:
                
                # If the losses don't cancel the gains and more
                if short_term_remaining >= abs(carry_forward):
                    
                    # Calculating the new tax and setting other important variables
                    short_term_tax_after = (short_term_remaining + carry_forward) * 0.2
                    short_term_remaining = (short_term_remaining + carry_forward)
                    carry_forward = 0
                    # print("7. ST CF if")
                
				# Otherwise there are still leftover losses
                else:
                    
					# Setting the remaining tax to 0 and setting other variables
                    short_term_tax_after = 0
                    carry_forward = short_term_remaining + carry_forward
                    short_term_remaining = 0
                    # print("7. ST CF else")

			# There are no more gains to offset
            else:
                # print("7. ST CF no gains")
                pass

        # If there are still more carry forward
        if carry_forward < 0:
            
			# Checking if there are any long term gains to offset
            if long_term_remaining > 0:
                
				# If the losses don't cancel the gains and more
                if long_term_remaining >= abs(carry_forward):
                    
                    # Calculating the new tax and setting other important variables
                    long_term_tax_after = (long_term_remaining + carry_forward) * 0.1
                    long_term_remaining	= (long_term_remaining + carry_forward)
                    carry_forward = 0
                    # print("8. LT CF if")
                
				# Otherwise there are still leftover losses
                else:
                    
					# Setting the remaining tax to 0 ans setting other variables
                    long_term_tax_after = 0
                    carry_forward = long_term_remaining + carry_forward
                    long_term_remaining = 0
                    # print("8. LT CF else")
                    
			# There are no more gains to offset
            else:
                # print("8. LT CF no gains")
                pass

        # Calculating the amount of losses left to carry forward 
        finalcarry = sum(gains)
        finalcarry = finalcarry + final_forward
        
		# Calculating the savings used to determine worth of harvest
        long_term_savings = long_term_tax_before - long_term_tax_after
        short_term_savings = short_term_tax_before - short_term_tax_after
        total_tax_before = long_term_tax_before + short_term_tax_before
        total_tax_after = long_term_tax_after + short_term_tax_after
        total_tax_savings = total_tax_before - total_tax_after
        try:
            total_tax_percentage_savings = (round(total_tax_savings / total_tax_before, 2)) * 100
        except ZeroDivisionError as e:
            total_tax_percentage_savings = 0
            print(e)
            pass
        
		# Calculating the gains
        total_gains_before = long_term_realised + short_term_realised
        total_gains_after = total_gains_before + long_term_unrealised + short_term_unrealised + min(og, 0)
        net_gains_before = total_gains_before - (total_tax_before)
        net_gains_after = total_gains_after - (total_tax_after)
        
        # Checking if the user wants printouts
        if print_info == True:
            
		    # Printing final after taxes and any carry forward losses
            print(f"LT after:            {long_term_tax_after}")
            print(f"ST after:            {short_term_tax_after}")
            print(f"LT saved:            {long_term_savings}")
            print(f"ST saved:            {short_term_savings}")
            print(f"Total savings:       {total_tax_savings}")
            print(f"Total savings:       %{total_tax_percentage_savings}")
            print(f"Gross gains before:  {total_gains_before}")
            print(f"Gross gains after:   {total_gains_after}")
            print(f"Net gains before:    {net_gains_before}")
            print(f"Net gains after:     {net_gains_after}")
            print(f"Carry forward:       {min(finalcarry, 0)}")
            
		# Returning the saving percentage, list of taxes and carry forward losses
        return total_tax_percentage_savings, [long_term_tax_before, short_term_tax_before, long_term_tax_after, short_term_tax_after], min(finalcarry, 0)