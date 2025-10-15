from sqlalchemy  import Column, Integer, String, Float
from .database import Base

class Movie(Base):
    __tablename__="movies"
    movie_Id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    genres = Column(String)
    
class Links(Base):
    __tablename__="links"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    movie_Id = Column(Integer )
    imdbId = Column(Integer)
    tmdbId = Column(Integer, nullable=True)
    
class Ratings(Base):
    __tablename__="ratings"
    id = Column(Integer)
    userId = Column(Integer, primary_key=True, index=True, autoincrement=True)
    movie_Id = Column(Integer)
    rating = Column(float)
    timestamp = Column(Integer)
    
class Tag(Base):
    __tablename__="tags"
    id = Column(Integer)
    userId = Column(Integer, primary_key=True, index=True, autoincrement=True)
    movie_Id = Column(Integer)
    tag = Column(String)
    timestamp = Column(Integer)
    