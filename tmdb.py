import http.client
import simplejson
#import json

class Tmdb():
	def __init__(self):
		self.connection = http.client.HTTPSConnection("api.themoviedb.org") # Gestionar posibles errores en el sprint 5
		self.payload = "{}"
		self.headers = { 'content-type': "application/json" }
		self.language = "es-ES"
		self.api_key = "c609321a0fc36c534c80b1b8c6928a32"
	
	# Receives a title and returns the id of the corresponding film in themoviedb or None if it does not exist
	def get_movie_id(self, title):
		title = title.replace(" ","%20")
		print("Searching " + title + "...")
		self.connection.request("GET", "/3/search/movie?query=" + title + "&language=" + self.language + "&api_key=" + self.api_key, self.payload, self.headers)
		res = self.connection.getresponse()
		jsondata = simplejson.load(res)
		if (jsondata["total_results"] == 0):
			print("No results")
			return None
		id = str(jsondata["results"][0].get('id'))
		print("Recommended title: " + jsondata["results"][0].get('title'))
		return id
		
	# Receives a list of films id's and returns a list of recommendations
	def get_recommendations(self, id_list):
		recommendations = []
		for movie_id in id_list:
			self.connection.request("GET", "/3/movie/" + movie_id + "/recommendations?language=" + self.language +
								"&api_key=" + self.api_key, self.payload, self.headers)
			res = self.connection.getresponse()
			jsondata = simplejson.load(res)
			i = 0
			print(jsondata["total_results"])
			for item in jsondata["results"]:
				name = item.get('title')
				date = item.get('release_date')
				rating = str(item.get('vote_average'))
				id = str(item.get('id'))
				recommendations.append([name, date, rating, id])
				i = i + 1
				if (i == 3):
					break
		return recommendations
					
	def close_connection(self):
		self.connection.close()
