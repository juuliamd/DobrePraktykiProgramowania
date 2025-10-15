from turtle import title
import fastapi
from pydantic import BaseModel
from typing import List, Optional
import csv


class Movies(BaseModel):
    movieId: int
    title: str
    genres: str
    
    class Config:
        from_attributes=True
    
class Links(BaseModel):
    movieId: int
    imdbId: int
    tmdbId: Optional[int]=None
    
    class Config:
        from_attributes = True

class Ratings(BaseModel):
    userId: int
    movieId: int
    rating: float
    timestamp: int
    
    class Config:
        from_attributes = True
    
class Tag(BaseModel):
    userId: int
    movieId: int
    tag: str
    timestamp: int
    
    class Config:
        from_attributes = True
    
    
    
app = fastapi.FastAPI()

movie_db = []
links_db=[]
ratings_db=[]
tags_db=[]


movies_file_name = 'movies.csv'
links_file = 'links.csv'
ratings_file = 'ratings.csv'
tags_file = 'tags.csv'

with open(movies_file_name, mode='r', encoding='utf-8') as file:
    csvFile = csv.DictReader(file)
    
    for lines in csvFile:
        lines['movieId'] = int(lines['movieId'])
        movie_db.append(lines)
        
with open(links_file, mode='r', encoding='utf-8') as file:
    csvFile = csv.DictReader(file)
    
    for lines in csvFile:
        lines['movieId'] = int(lines['movieId'])
        lines['imdbId'] = int(lines['imdbId'])
        if lines['tmdbId']:
            lines['tmdbId'] = int(lines['tmdbId'])
        else:
            lines['tmdbId'] = None
        links_db.append(lines)
        
with open(ratings_file, mode='r', encoding='utf-8') as file:
    csvFile = csv.DictReader(file)
    
    for lines in csvFile:
        lines['userId'] = int(lines['userId'])
        lines['movieId'] = int(lines['movieId'])
        lines['rating'] = float(lines['rating'])
        lines['timestamp'] = int(lines['timestamp'])
        ratings_db.append(lines)
        
with open(tags_file, mode='r', encoding='utf-8') as file:
    csvFile = csv.DictReader(file)
    
    for lines in csvFile:
        lines['userId'] = int(lines['userId'])
        lines['movieId'] = int(lines['movieId'])
        lines['timestamp'] = int(lines['timestamp'])
        tags_db.append(lines)
        
        

@app.get("/")
def read_root():
    return {"message": "Movie database"}

@app.get("/movies", response_model=List[Movies])
def get_all_movies():
    return movie_db

@app.get("/movies/show-dict/{movie_id}")
def show_movie_dict(movie_id: int):
    found_movie = None
    for movie_data in movie_db:
        if movie_data['movieId']==movie_id:
            found_movie = movie_data
            break
    if not found_movie:
        return {"message": "Movie not found"}
    
    movie_object = Movies(**found_movie)
    return movie_object.__dict__

@app.get("/links", response_model=List[Links])
def get_all_links():
    return links_db

@app.get("/ratings", response_model=List[Ratings])
def get_all_ratings():
    return ratings_db   

@app.get("/tags", response_model=List[Tag])
def get_all_tags():
    return tags_db