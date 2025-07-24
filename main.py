from pypresence import Presence
import time
# import random
import os
import requests
# from bs4 import BeautifulSoup

import json

###############################################################################
# Config                                                                      #
###############################################################################
## Coupon Getter
# Prevent downloading the coupon page if cache is yonger than maxHours
maxHours = 4

# Coupon page url
url = "https://www.dominos.com.au/offers/"

# Cached coupon page filename
cache = "cache"+".html"

# Spoof html headers
useragent = "Mozilla/5.0 (X11; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0"
accept = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
accept_encoding = "gzip, deflate, br, zstd"
accept_language = "en-US,en;q=0.5"

## Discord Status
# Client ID
client_id = '494387497472622603'
###############################################################################

maxSeconds = maxHours*60*60
def filetime(path):
	try:
		return time.time() - os.path.getmtime(path)
	except:
		return maxSeconds + 1

if filetime(cache) > maxSeconds:
	print("Cached webpage too old, updating...")
	with open(cache, "w") as f:
		f.write(requests.get(
			url, 
			headers={
				"Accept":accept,
				"Accept-Encoding":accept_encoding,
				"Accept-Language":accept_language,
				"Dnt":"1",
				"Upgrade-Insecure-Requests":"1",
				"User-Agent":useragent
				}).text)
else:
	print("Using cached webpage.")

with open(cache, "r") as f:
	print("Parsing html...")
	soup = BeautifulSoup(f.read(), "html.parser")
	# deals = soup.select(".special-offer-anz.item .offer-ribbon-anz")
	# codes = soup.select(".special-offer-anz.item .offer-code-anz p")

	deals = soup.select(".localOfferContent .localTitle")
	codes = soup.select(".localOfferContent .copyVoucher")

	coupons = []

	if deals and codes:
		print("Found Coupons: ")
		for coupon in zip(deals, codes):
			formatted_deal = coupon[0].get_text().strip().replace(" Pick-Up/Delivered *","").replace("Pick-Up *","")
			formatted_deal = formatted_deal[:125] + (formatted_deal[125:] and '...')
			formatted_code = coupon[1].get("data-voucher")

			coupons.append([formatted_deal,formatted_code]) 
			print("Deal: {0}, Code: {1}".format(formatted_deal,formatted_code))
	else:
		print("Couldn't locate coupons :(")

def ready(coupons):
	print("Connecting to discord...")
	RPC = Presence(client_id)  # Initialize the Presence class
	RPC.connect()  # Start the handshake loop

	detail = 0

	states=[]
	details=[]
	
	for coupon in coupons:
		states.append(coupon[1])
		details.append(coupon[0])

	start=None
	end=None
	large_image=["cheese","hamandcheese","hawaiian"]
	large_text=["Cheese","Ham & Cheese","Hawaiian"]
	small_image="dominos"
	small_text="Domino's Pizza"
	party_id=None
	party_size=None#[3,8]

	while True:  # The presence will stay on as long as the program is running
		if detail >= len(details):
			detail = 0
		RPC.update(details=details[detail], state=states[detail], start=start, end=end, large_image=large_image[detail], large_text=large_text[detail], small_image=small_image, small_text=small_text,party_id=party_id,party_size=party_size) #Set the presence, picking a random quote
		time.sleep(10) #Wait a wee bit
		detail += 1

if coupons:
	ready(coupons)