#!/usr/bin/env python3

import cherrypy
import json
from collections import defaultdict
import os
import ast


class Movie_Controller:
    def __init__(self, database_controller):
        self.database_controller = database_controller
    
    def get_movies(self):
        output = {
            "result": "success"
        }

        # Return all movies
        movies_with_string_genres = [{'id': mid, 'title': movie['title'], 'genres': '|'.join(movie['genres'])} for mid, movie in self.database_controller.movies.items()]

        output["movies"] = movies_with_string_genres

        return json.dumps(output)
    
    def post_movies(self):
        body = cherrypy.request.body.read().decode('utf-8')
        body = json.loads(body)

        # Add a new movie        
        title = body['title']
        genres = body['genres'].split('|')
        movie_id = max(self.database_controller.movies) + 1

        self.database_controller.movies[movie_id] = {
            'title': title,
            'genres': genres,
            'ratings': []
        }

        output = {"result": "success", "id": movie_id}

        return json.dumps(output)

    def delete_movies(self):
        # Delete all movies
        self.database_controller.movies.clear()

        return json.dumps({"result": "success"})

    def get_movie_id(self, movie_id):
        # Return a single movie by movie_id
        movie_id = int(movie_id)
        movie = self.database_controller.movies.get(movie_id)
        movie_img = self.database_controller.get_image_for_movie(movie_id)

        output = {"result": "success"}

        if not movie:
            output["result"] = "error"

            return json.dumps(output)

        movie_genres = movie["genres"]

        # if len(movie_genres) > 1:
            # print(f"greater than 1!!!!")
        movie_genres = '|'.join(movie_genres)

        output["genres"] = movie_genres
        output["title"] = movie["title"]
        output["id"] = movie_id
        output["img"] = movie_img

        return json.dumps(output)
            
    def put_movie_id(self, movie_id=None):
        body = cherrypy.request.body.read().decode('utf-8')
        body = json.loads(body)

        movie_id = int(movie_id)

        title = body['title']
        genres = body['genres'].split('|')

        self.database_controller.movies[movie_id] = {
            'title': title,
            'genres': genres,
        }

        return json.dumps({"result": "success"}) 

    def delete_movies_id(self, movie_id=None):
        movie_id = int(movie_id)
        if movie_id in self.database_controller.movies:
            del self.database_controller.movies[movie_id]
            return json.dumps({"result": "success"})
        
        return json.dumps({"result": "error", "message": "Movie not found"})
