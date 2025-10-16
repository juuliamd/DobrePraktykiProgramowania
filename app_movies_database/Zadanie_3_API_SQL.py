import fastapi
from typing import List
from sqlalchemy.orm import Session
from database import SessionLocal
import models as models
from pydantic import BaseModel
from typing import Optional


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

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
    

@app.get("/")
def read_root():
    return {"message": "baza danych filmów oparta na SQLite i SQLAlchemy"}

@app.get("/movies", response_model=List[Movies])
def get_all_movies(db: Session = fastapi.Depends(get_db)):
    movies = db.query(models.Movie).all()
    return movies

@app.get("/links", response_model=List[Links])
def get_all_links(db: Session = fastapi.Depends(get_db)):
    links = db.query(models.Links).all()
    return links

@app.get("/ratings", response_model=List[Ratings])
def get_all_ratings(db: Session = fastapi.Depends(get_db)):
    ratings = db.query(models.Ratings).all()
    return ratings  

@app.get("/tags", response_model=List[Tag])
def get_all_tags(db: Session = fastapi.Depends(get_db)):
    tags=db.query(models.Tag).all()
    return tags