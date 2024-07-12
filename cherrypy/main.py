#!/usr/bin/env python3

import cherrypy
import json
from collections import defaultdict
import os
import ast

class MovieDatabase:
    def __init__(self):
        self.data_directory = '/escnfs/courses/fa23-cse-30332.01/public/cherrypy/data/'
        self.movies = self.load_movies()
        self.users = self.load_users()
        self.ratings = self.load_ratings()
        self.images = self.load_images()

    def load_dat_file(self, filename):
        filepath = os.path.join(self.data_directory, filename)
        with open(filepath, 'r') as file:
            content = file.read().splitlines()
        return content

    def load_movies(self):
        movies_content = self.load_dat_file('movies.dat')
        movies = {}
        for line in movies_content:
            movie_id, title, genres = line.split('::')
            movies[int(movie_id)] = {
                'title': title,
                'genres': genres.split('|'),
                'ratings': []
            }
        return movies

    def load_users(self):
        users_content = self.load_dat_file('users.dat')
        users = {}
        for line in users_content:
            user_id, gender, age, occupation, zipcode = line.split('::')
            users[int(user_id)] = {
                'gender': gender,
                'age': int(age),
                'id': int(user_id),
                'occupation': int(occupation),
                'zipcode': zipcode,
                'rated_movies': []
            }
        return users

    def load_ratings(self):
        ratings_content = self.load_dat_file('ratings.dat')
        ratings = {}
        for line in ratings_content:
            user_id, movie_id, rating, timestamp = line.split('::')
            user_id, movie_id, rating = int(user_id), int(movie_id), float(rating)
            if movie_id not in ratings:
                ratings[movie_id] = []
            ratings[movie_id].append(rating)
            if user_id in self.users:  # Update rated movies for the user
                self.users[user_id]['rated_movies'].append(movie_id)
        return ratings

    def load_images(self):
        images_content = self.load_dat_file('images.dat')
        images = {}
        for line in images_content:
            movie_id, _, img = line.split('::')
            images[int(movie_id)] = img
        return images

    def get_average_ratings(self):
        average_ratings = {}
        for movie_id, ratings in self.ratings.items():
            average_ratings[movie_id] = sum(ratings) / len(ratings) if ratings else 0
        return average_ratings
    
    def sort_dict_by_value_then_key(self, input_dict):
        # Sort the dictionary by value in descending order, then by key in ascending order
        sorted_items = sorted(input_dict.items(), key=lambda item: (-item[1], item[0]))
        # The first item will be the one with the highest value and, in case of a tie, the lowest key
        return sorted_items[0][0]
    
    
    def add_or_update_rating(self, user_id, movie_id, rating):
        # Check if the user and movie exist
        user = self.users.get(user_id)
        movie = self.movies.get(movie_id)

        print(user)
        print(movie)

        # If the user or movie does not exist, return None
        if not user or not movie:
            print("returning none")
            return None

        # Convert rating to float to maintain consistency
        rating = float(rating)

        # Check if the user has already rated the movie
        if movie_id in user['rated_movies']:
            print("movie already dated")
            # Find the existing rating index for the movie
            for i, r in enumerate(movie['ratings']):
                if self.ratings[movie_id][i][0] == user_id:  # Assuming ratings are stored as (user_id, rating)
                    # Update the existing rating
                    movie['ratings'][i] = (user_id, rating)
                    break
        else:
            # The user has not yet rated the movie, so add the rating
            print("new rating")
            movie['ratings'].append((user_id, rating))
            user['rated_movies'].append(movie_id)

        # Update the ratings dictionary
        self.ratings[movie_id] = movie['ratings']  # Update the ratings list for the movie_id

        # Return an acknowledgment
        return "Rating added/updated successfully."



    def recommend_movie_for_user(self, user_id):
        user = self.users.get(user_id)
        if not user:
            return None  # User not found
        rated_movies = set(user['rated_movies'])
        average_ratings = self.get_average_ratings()

        # Filter out movies the user has rated and sort by average rating
        unrated_movies = {k: v for k, v in average_ratings.items() if k not in rated_movies}
        recommended_movie_id = self.sort_dict_by_value_then_key(unrated_movies)

        return recommended_movie_id
    
    

def string_to_dict(s):
    entries = s.strip('{}').split(', ')
    result = {}   
    for entry in entries:
        key, value = entry.split(': ')
        key = key.strip('”“"')
        if value.startswith('”') or value.startswith('"'):
            value = value.strip('”“"')
        elif '.' in value:
            value = float(value)
        elif value.isdigit():
            value = int(value)
        else:
            value = value.strip('”“"')
        
        result[key] = value
    
    return result


class MyController:
    def __init__(self):
        self.db = MovieDatabase()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def movies(self, movie_id=None):
        if cherrypy.request.method == 'GET':
            if movie_id is None:
                # Return all movies
                movies_with_string_genres = [{'id': mid, 'title': movie['title'], 'genres': '|'.join(movie['genres'])} for mid, movie in self.db.movies.items()]
                return {'movies': movies_with_string_genres}
            else:
                # Return a single movie by movie_id
                movie_id = int(movie_id)
                movie = self.db.movies.get(movie_id)
                if movie:
                    # Modify the movie dictionary to join genres into a string
                    movie_with_string_genres = movie.copy()
                    if isinstance(movie['genres'], str) and '|' in movie['genres']:
                        movie['genres'] = movie['genres'].split('|')
                    movie_with_string_genres['genres'] = '|'.join(movie['genres'])
                    # Assuming images are loaded and available in the movies dictionary
                    movie_with_string_genres['img'] = self.db.images.get(movie_id, '')
                    return movie_with_string_genres
                else:
                    return {"result": "error", "message": "Movie not found"}

        elif cherrypy.request.method == 'DELETE':
                try:
                    if movie_id is None:
                        # Delete all movies
                        self.db.movies.clear()
                        return {"result": "success"}
                    else:
                        movie_id = int(movie_id)
                        if movie_id in self.db.movies:
                            del self.db.movies[movie_id]
                            return {"result": "success"}
                        else:
                            return {"result": "error", "message": "Movie not found"}
                except ValueError:
                    return {"result": "error", "message": "Invalid movie_id"}
                except Exception as e:  # Catch all other exceptions
                    return {"result": "error", "message": str(e)}
        
        else: 
            # Read and parse the request body if method is POST, PUT or DELETE like the movies function does 
            body = cherrypy.request.body.read().decode('utf-8')
            body_dat = string_to_dict(body)


            if cherrypy.request.method == 'POST':
                # Add a new movie        
                title = body_dat['title']
                genres = body_dat['genres'].split('|')
                movie_id = max(self.db.movies) + 1
                self.db.movies[movie_id] = {
                    'title': title,
                    'genres': genres,
                    'ratings': []
                }
                return {"result": "success", "id": movie_id}
                

            elif cherrypy.request.method == 'PUT':
                # Update an existing movie
                movie_id = int(movie_id)
                if movie_id not in self.db.movies:
                    return {"result": "error", "message": "Movie not found"}

                title = body_dat['title']
                genres = body_dat['genres']

                self.db.movies[movie_id] = {
                    'title': title,
                    'genres': genres,
                    #'ratings': self.db.movies[movie_id].get('ratings', [])
                }
                return {"result": "success"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def users(self, user_id=None):

        if cherrypy.request.method == 'GET':
            if user_id is None:
                return {"users": list(self.db.users.values())}
            else:
                user_id = int(user_id)
                user = self.db.users.get(user_id)
                if user:
                    return user
                else:
                    return {"result": "error", "message": "User not found"}

        elif cherrypy.request.method == 'DELETE':
                if user_id is None:
                    self.db.users.clear()
                    return {"result": "success"}
                else:
                    try:
                        user_id = int(user_id)
                        if user_id in self.db.users:
                            del self.db.users[user_id]
                            return {"result": "success"}
                        else:
                            raise cherrypy.HTTPError(404, "User not found")
                    except ValueError:
                        raise cherrypy.HTTPError(400, "Invalid user_id")

        else:
            # Read and parse the request body if method is POST, PUT or DELETE
            body = cherrypy.request.body.read().decode('utf-8')
            body_data = string_to_dict(body)

            if cherrypy.request.method == 'POST':
                try:
                    gender = body_data['gender']
                    age = int(body_data['age'])
                    occupation = int(body_data['occupation'])
                    zipcode = body_data['zipcode']
                    user_id = max(self.db.users) + 1
                    self.db.users[user_id] = {
                        'id': int(user_id),
                        'gender': gender,
                        'age': age,
                        'occupation': occupation,
                        'zipcode': zipcode,
                        'rated_movies': []
                    }
                    return {"result": "success", "id": user_id}
                except KeyError as e:
                    raise cherrypy.HTTPError(400, "Missing parameter: " + str(e))

            elif cherrypy.request.method == 'PUT':
                user_id = int(user_id)
                if user_id not in self.db.users:
                    return {"result": "error", "message": "User not found"}

                if 'gender' in body_data:
                    gender = body_data['gender']
                    self.db.users[user_id] = {'gender': gender}
                if 'age' in body_data:
                    age = body_data['age']
                    self.db.users[user_id] = {'age': age}
                if 'occupation' in body_data:
                    occupation = body_data['occupation']
                    self.db.users[user_id] = {'occupation': occupation}
                if 'zipcode' in body_data:
                    zipcode = body_data['zipcode']
                    self.db.users[user_id] = {'zipcode': zipcode}
                
                
                self.db.users[user_id] = {
                    'id': user_id,
                    'gender': gender,
                    'age': age,
                    'occupation': occupation,
                    'zipcode': zipcode,
                    #'rated_movies': self.db.users[user_id]['rated_movies'] NOT TOO SURE ABOUT THIS LINE MIGHT HAVE TO DELETE
                }
                return {"result": "success"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def recommendations(self, user_id=None):
        
        if cherrypy.request.method == 'GET':
            if user_id is None:
                raise cherrypy.HTTPError(400, "ERROR: User ID is required for recommendations")
            else:
                user_id = int(user_id)
                recommendation = self.db.recommend_movie_for_user(user_id)
                if recommendation:
                    return {"user_id": user_id, "movie_id": recommendation}
                else:
                    raise cherrypy.HTTPError(404, "ERROR: No recommendation found or user not found")

        elif cherrypy.request.method == 'PUT': 
            if user_id is None:
                raise cherrypy.HTTPError(400, "ERROR: User ID is required for recommendations")
            else:
                body = cherrypy.request.body.read().decode('utf-8')
                body_data = string_to_dict(body)
                movie_id = int(body_data['movie_id'])
                rating = int(body_data['rating'])
                
                
                if user_id is None or movie_id is None or rating is None:
                    raise cherrypy.HTTPError(400, "Required data not provided")
                # Assuming there's a method in your db to add/update ratings
                print("going in")
                self.db.add_or_update_rating(user_id, movie_id, rating)
                return {"result": "success"}
                
        elif cherrypy.request.method == 'DELETE':
            try:
                self.db.ratings.clear()
                for user in self.db.users.values():
                    user['rated_movies'].clear()
                return {"result": "success"}
            except Exception as e:
                return {"result": "error", "message": str(e)}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def ratings(self, movie_id=None):
        if cherrypy.request.method == 'GET':
            if movie_id is None:
                raise cherrypy.HTTPError(400, "ERROR: Movie ID is required for ratings")
            else:
                movie_id = int(movie_id)
                average_rating = self.db.get_average_ratings().get(movie_id)
                if average_rating is not None:
                    return {"movie_id": movie_id, "rating": average_rating, "result": "success"}
                else:
                    raise cherrypy.HTTPError(404, "ERROR: Movie not found")

    @cherrypy.expose
    @cherrypy.expose
    def reset(self):
        if cherrypy.request.method == 'PUT':
            # Reload all data from the files
            self.db.movies = self.db.load_movies()
            self.db.users = self.db.load_users()
            self.db.ratings = self.db.load_ratings()
            self.db.images = self.db.load_images()
            return {"result": "success"}

mycont = MyController()
dispatcher = cherrypy.dispatch.RoutesDispatcher()

# Connect endpoints to dispatcher
dispatcher.connect('movies', '/movies/', controller=mycont, action='movies', conditions=dict(method=['GET', 'POST', 'DELETE']))
dispatcher.connect('movie_detail', '/movies/:movie_id', controller=mycont, action='movies', conditions=dict(method=['GET', 'PUT', 'DELETE']))
dispatcher.connect('users', '/users/', controller=mycont, action='users', conditions=dict(method=['GET', 'POST', 'DELETE']))
dispatcher.connect('user_detail', '/users/:user_id', controller=mycont, action='users', conditions=dict(method=['GET', 'PUT', 'DELETE']))
dispatcher.connect('recommendations', '/recommendations/', controller=mycont, action='recommendations', conditions=dict(method=['DELETE']))
dispatcher.connect('recommendations_detail', '/recommendations/:user_id', controller=mycont, action='recommendations', conditions=dict(method=['GET', 'PUT']))
dispatcher.connect('ratings', '/ratings/:movie_id', controller=mycont, action='ratings', conditions=dict(method=['GET']))
dispatcher.connect('reset', '/reset/', controller=mycont, action='reset', conditions=dict(method=['PUT']))

conf = {
    'global': {
        'server.socket_host': 'student04.cse.nd.edu', 
        'server.socket_port': 52015}, '/': {
        'request.dispatch': dispatcher}
}

cherrypy.config.update(conf)
app = cherrypy.tree.mount(None, config=conf)
cherrypy.quickstart(app)
