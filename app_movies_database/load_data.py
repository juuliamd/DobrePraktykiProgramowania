import csv
from database import SessionLocal, engine
import models as models

models.Base.metadata.create_all(bind=engine)

db=SessionLocal()

def load_csv_data(filename, model_class, type_conversions):
    print(f"Loading data from {filename}...")
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            for key, func in type_conversions.items():
                if row.get(key):
                    try: 
                        row[key] = func(row[key])
                    except (ValueError, TypeError):
                        row[key]=None
                else:
                    row[key]= None

            db.object = model_class(**row)
            db.add(db.object)
    db.commit()
    print(f"Data from {filename} loaded successfully")
    
movies_types = {'movieId': int}
links_types = {'movieId': int, 'imdbId': int, 'tmdbId': int}
ratings_types = {'userId': int, 'movieId': int, 'rating': float, 'timestamp': int}
tags_types = {'userId': int, 'movieId': int, 'timestamp': int}

load_csv_data('movies.csv', models.Movie, movies_types)
load_csv_data('links.csv', models.Links, links_types)
load_csv_data('ratings.csv', models.Ratings, ratings_types)
load_csv_data('tags.csv', models.Tag, tags_types)

db.close()