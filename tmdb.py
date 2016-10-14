import http.client
import simplejson

class Tmdb():
    def __init__(self):
        self.payload = "{}"
        self.headers = { 'content-type': "application/json" }
        self.language = "es-ES"
        self.api_key = "c609321a0fc36c534c80b1b8c6928a32"
        try:
            self.connection = http.client.HTTPSConnection("api.themoviedb.org", timeout=6) # Gestionar posibles errores en el sprint 5
            print("Conexión establecida")
        except http.client.HTTPException:
            print("Error al conectarse con la base de datos")
	
	# Receives a title and returns the id of the corresponding film in themoviedb or None if it does not exist
    def get_movie_id(self, title):
        title = title.replace(" ","%20")
        print("Searching " + title + "...")
        try :
            self.connection.request("GET", "/3/search/movie?query=" + title + "&language=" + self.language + "&api_key=" + self.api_key, self.payload, self.headers)
            res = self.connection.getresponse()
            jsondata = simplejson.load(res)
            if (jsondata["total_results"] == 0):
                print("No results")
                return None
            id = str(jsondata["results"][0].get('id'))
            print("Recommended title: " + jsondata["results"][0].get('title'))
            return id
        except Exception:
            print("Error al conectarse a la base de datos")
            return None
		
	# Receives a list of films id's and returns a list of recommendations
    def get_recommendations(self, id_list):
        recommendations = []
        for movie_id in id_list:
            try:
                self.connection.request("GET", "/3/movie/" + movie_id + "/recommendations?language=" + self.language +
                                        "&api_key=" + self.api_key, self.payload, self.headers)
                res = self.connection.getresponse()
                jsondata = simplejson.load(res)
                i = 0
                for item in jsondata["results"]:
                    name = item.get('title')
                    date = item.get('release_date')
                    rating = str(item.get('vote_average'))
                    id = str(item.get('id'))
                    recommendations.append([name, date, rating, id])
                    i = i + 1
                    if (i == 3):
                        break
            except Exception:
                break
        return recommendations
			
            		
    def close_connection(self):
        self.connection.close()
