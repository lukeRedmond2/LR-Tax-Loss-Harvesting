# Importing necessary imports
import requests
from bs4 import BeautifulSoup as bs
import yfinance as yf
from datetime import datetime, timedelta

# DataLoader class
class DataLoader():
    
	# Initialiser
    def __init__(self):
        pass
    
	# Live data scraper
    def Live(self, symbol, choice):
        
		# Checking if price is chosen
        if choice == "price":
            
			# Setting variables to access the data
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}
            url = f"https://finance.yahoo.com/quote/{symbol}"
            
			# Extracting and parsing the HTML code
            request = requests.get(url, headers=headers)
            htmlcode = bs(request.text, "html.parser")
            
			# Finding and returning the price
            return float(htmlcode.find("fin-streamer", {"class": "livePrice svelte-mgkamr"}).text.replace(",", ''))

		# Checking if market capitalisation is chosen
        elif choice == "mcap":

			# Setting variables to access the data
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}
            url = f"https://finance.yahoo.com/quote/{symbol}"

			# Extracting and parsing the HTML code
            request = requests.get(url, headers=headers)
            htmlcode = bs(request.text, "html.parser")

            # Extracting the market capitalisation expression
            cap = (htmlcode.find("fin-streamer", {"data-field": "marketCap"}).text.replace(" ", ''))    
            
			# Creating a dictionary of suffix multipliers
            multipliers = {
            	'K': 1000,
            	'M': 1000000,
        		'B': 1000000000,
        		'T': 1000000000000
            }
            
			# Checking if there is suffix on the extracted expression
            if cap[-1] in multipliers:
                
				# Extracting and using the multiplier
                multiplier = multipliers[cap[-1]]
                value = float(cap[:-1]) * multiplier
                return int(value)
            
			# Otherwise there's no suffix so returning the raw extraction
            else:
                
                # Converting the cap to a float
                return float(cap)
            
    # Past data scraper
    def Past(self, universe):

		# Download and extract the close data
        data = yf.download(universe, start=datetime.today()-timedelta(30), end=datetime.today())
        closes = data["Close"]
        
		# Returning the close prices
        return closes