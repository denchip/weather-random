import requests
import json
import random
import hashlib
import bencode
import random

API_KEY = 'a9ce90b7ca65e0a3a1dd4fd0efa5927f'

def get_response():
	lat = random.randint(0, 160) - 80
	lon = random.randint(0, 360) - 180
	response = requests.get(' http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&APPID={}'.format(lat, lon, API_KEY)).json()
	response_md5 = hashlib.md5(bencode.Bencoder.encode(response).encode('utf-8')).hexdigest()
	response_as_int = int(response_md5, 16)
	return response_as_int

def randint(a, b):
	try:	
		a = int(a)
		b = int(b) + 1
		a, b = min(a, b), max(a, b)
		c = 1 % b
	except:
		print('Incorrect values')
		return
	return a + get_response() % b
