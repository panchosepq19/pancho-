#!/usr/bin/env python3

import cherrypy
import json
from collections import defaultdict
import os
import ast


class Data_Controller:
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
            ratings[movie_id].append((rating, user_id))
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
    
    def get_image_for_movie(self, movie_id):
        if movie_id not in self.images:
            return ""

        return self.images[movie_id]

    def get_average_ratings(self):
        average_ratings = {}
        for movie_id, ratingObject in self.ratings.items():
            ratings = [rating[0] for rating in ratingObject]
            average_ratings[movie_id] = sum(ratings) / len(ratings) if ratings else 0
        return average_ratings
    
    def sort_dict_by_value_then_key(self, input_dict):
        # Sort the dictionary by value in descending order, then by key in ascending order
        sorted_items = sorted(input_dict.items(), key=lambda item: (-item[1], item[0]))
        # The first item will be the one with the highest value and, in case of a tie, the lowest key
        return sorted_items[0][0]
    
    
    def add_or_update_rating(self, user_id, movie_id, rating):
        user = self.users.get(user_id)
        movie = self.movies.get(movie_id)

        if not user or not movie:
            return None

        rating = float(rating)

        if movie_id in user['rated_movies']:

            allRatingObjects = self.ratings[movie_id]

            for index in range(len(allRatingObjects)):
                if allRatingObjects[index][1] == user_id:
                    self.ratings[movie_id][index] = (rating, user_id)
                    break
        else:
            movie['ratings'].append((user_id, rating))
            user['rated_movies'].append(movie_id)

    def recommend_movie_for_user(self, user_id):
        user = self.users.get(user_id)
        if not user:
            return None  # User not found
        rated_movies = set(user['rated_movies'])
        average_ratings = self.get_average_ratings()

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