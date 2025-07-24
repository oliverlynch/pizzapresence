from pypresence import Presence
import time
import os
import requests

import json5
import re

###############################################################################
# Config                                                                      #
###############################################################################
## Coupon Getter
# Prevent downloading the coupon page if cache is younger than maxHours
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
				"Accept-Language":accept_language,
				"Dnt":"1",
				"Upgrade-Insecure-Requests":"1",
				"User-Agent":useragent
				}).text)
else:
	print("Using cached webpage.")

with open(cache, "r") as f:

	fl = f.read();

	st = fl.find("nationalDeals: [")
	ed = fl.find("]", st)

	nationalDealString = fl[st + 15:ed + 1]

	# Remove comments
	nationalDealString = re.sub(r"\s\/\/.*$", "", nationalDealString, flags=re.MULTILINE);
	nationalDealString = nationalDealString.replace("'",'"')

	# Attempt parsing as json
	nationalDeals = json5.loads(nationalDealString);

	coupons = []
	for coupon in nationalDeals:
		dealCode = coupon["cta_link"][-6:]
		link = [{"url":coupon["cta_link"], "label": "Order Now"}]

		coupons.append([coupon["desc"], dealCode, link])
		print("Deal: {0}, Code: {1}, Link: {2}".format(coupon["desc"],dealCode,link))

def ready(coupons):
	print("Connecting to discord...")
	RPC = Presence(client_id)  # Initialize the Presence class
	RPC.connect()  # Start the handshake loop

	start=time.time()
	large_image=["cheese","hamandcheese","hawaiian"]
	large_text=["Cheese","Ham & Cheese","Hawaiian"]
	small_image="dominos"
	small_text="Domino's Pizza"
	party_id=None
	party_size=None#[3,8]

	i = 0

	while True:  # The presence will stay on as long as the program is running
		c = i % len(coupons)
		l = i % len(large_image)
		RPC.update(details=coupons[c][0], state=coupons[c][1], buttons=coupons[c][2], start=start, end=time.time() + 11, large_image=large_image[l], large_text=large_text[l], small_image=small_image, small_text=small_text,party_id=party_id,party_size=party_size) #Set the presence, picking a random quote
		time.sleep(10) #Wait a wee bit
		i += 1

if coupons:
	ready(coupons)