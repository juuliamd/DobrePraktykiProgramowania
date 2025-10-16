from sqlalchemy  import Column, Integer, String, Float
from database import Base

class Movie(Base):
    __tablename__="movies"
    movieId = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    genres = Column(String)
    
class Links(Base):
    __tablename__="links"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    movieId = Column(Integer )
    imdbId = Column(Integer)
    tmdbId = Column(Integer, nullable=True)
    
class Ratings(Base):
    __tablename__="ratings"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userId = Column(Integer)
    movieId = Column(Integer)
    rating = Column(Float)
    timestamp = Column(Integer)
    
class Tag(Base):
    __tablename__="tags"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userId = Column(Integer)
    movieId = Column(Integer)
    tag = Column(String)
    timestamp = Column(Integer)
    