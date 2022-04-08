import pandas as pd
from pathlib import Path
pd.set_option("display.max_rows", None, "display.max_columns", None)

output_file = 'movies.csv'
output_dir = Path('data')

output_dir.mkdir(parents=True, exist_ok=True)

# Movie class constructor
class Movie:
    # Constructor
    def __init__(self, series_title, released_year, runtime, genre, IMDB_rating, overview,
                 meta_score, director, star1, star2, star3, star4, no_of_votes):

        self.series_title = series_title
        self.released_year = released_year
        self.runtime = runtime
        self.genre = genre
        self.IMDB_rating = IMDB_rating
        self.overview = overview
        self.meta_score = meta_score
        self.director = director
        self.star1 = star1
        self.star2 = star2
        self.star3 = star3
        self.star4 = star4
        self.no_of_votes = no_of_votes


    def __str__(self):  # overwrite print(Movie) otherwise it will print object reference
        return "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (
            self.series_title, self.released_year, self.runtime, self.genre,
            self.IMDB_rating, self.overview, self.meta_score, self.director, self.star1, self.star2, self.star3,
            self.star4, self.no_of_votes
        )
    # Method to load movie data from cvs
    def load_movie_data(table):
        # Movie Dataframe
        movies_df = pd.read_csv(output_dir / output_file, encoding="ISO-8859-1")
        # Converts Row of Data into Dictionaries
        movie_list = movies_df.to_dict(orient='records')
        # Loop Through Movie Data and Create Movie Objects
        for movie in movie_list:
            series_title = movie['Series_Title']
            released_year = movie['Released_Year']
            runtime = movie['Runtime']
            genre = movie['Genre']
            IMDB_rating = movie['IMDB_Rating']
            overview = movie['Overview']
            meta_score = movie['Meta_Score']
            director = movie['Director']
            star1 = movie['Star1']
            star2 = movie['Star2']
            star3 = movie['Star3']
            star4 = movie['Star4']
            no_of_votes = movie['No_of_Votes']

            # Movie Object
            movie = Movie(series_title, released_year, runtime, genre, IMDB_rating,
                          overview, meta_score, director, star1, star2, star3, star4, no_of_votes)

            # Insert into Dictionary
            table.append(movie)
