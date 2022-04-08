import matplotlib
# Agg needed for main loop crash
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import load_data
from load_data import *
import functions
import io
import base64
import pandas as pd
import seaborn as sns
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from fuzzywuzzy import process
from pathlib import Path

pd.set_option("display.max_rows", None, "display.max_columns", None)
# File Information
output_file = 'movies.csv'
output_dir = Path('data')
output_dir.mkdir(parents=True, exist_ok=True)
# Retrieving Columns
movie_data = pd.read_csv(output_dir / output_file, usecols=['Series_Title', 'IMDB_Rating', 'No_of_Votes'],
                         dtype={'Series_Title': 'str', 'IMDB_Rating': 'float', 'No_of_Votes': 'int32'},
                         encoding='latin-1')

sns.set(font_scale=1)
plt.rcParams['axes.grid'] = False


# Generate scatterpoint cluster image
def cluster_pic():
    cluster_to_IObytes = io.BytesIO()

    plot = sns.jointplot(x='IMDB_Rating', y='No_of_Votes', data=movie_data, alpha=0.5, color='tab:blue')
    plot.set_axis_labels('IMDB Rating', 'Number of Votes', fontsize=16)
    plot.savefig(cluster_to_IObytes, format='png', bbox_inches='tight')
    plt.close()

    pd.set_option('display.float_format', lambda x: '%.3f' % x)

    # Encode PNG image to base64 string
    return base64.b64encode(cluster_to_IObytes.getvalue()).decode('utf-8')


# Generate pie image
def pie_pic(title, type):
    # Loop through movie list
    for m in movie_list:
        # Returns match
        if m.series_title == title:
            donut_to_IObytes = io.BytesIO()

            # Donut chart labels and percentages

            # IMDB
            if type == 'imdb':
                sizes = [m.IMDB_rating, 10 - m.IMDB_rating]
                colors = ['#F4E409', '#8F93A3']

            # Meta
            if type == 'meta':
                sizes = [m.meta_score, 100 - m.meta_score]
                colors = ['#8F93A3', '#f06800']

            explode = (0, 0.1)

            fig, ax = plt.subplots()
            ax.pie(sizes,
                   explode=explode,
                   colors=colors,
                   autopct='%1.1f%%',
                   shadow=True,
                   startangle=90,
                   )

            centre_circle = plt.Circle((0, 0), 0.5, color='black',
                                       fc='white', linewidth=0)

            plt.legend(loc='lower left', labels=['Approval', 'Disapproval'], prop={'size': 11}, bbox_to_anchor=(0.2, 0),
                       bbox_transform=fig.transFigure)

            fig = plt.gcf()
            fig.gca().add_artist(centre_circle)

            # Equal aspect ratio to ensure circular donut chart
            ax.axis('equal')
            # IMDB image title
            if type == 'imdb':
                ax.set_title(m.series_title.title() + ' IMDB Approval Rating')
            # Meta image title
            if type == 'meta':
                ax.set_title(m.series_title.title() + ' Metascore Rating')

            # Grade Scores
            score = functions.score(m)
            meta_score = functions.meta_score(m)

            # Grade scoring inside donut chart
            if type == 'imdb':
                ax.text(0.5, 0.5, score, horizontalalignment='center', verticalalignment='center', size=40,
                        fontweight=600,
                        transform=ax.transAxes)
            if type == 'meta':
                ax.text(0.5, 0.5, meta_score, horizontalalignment='center', verticalalignment='center', size=40,
                        fontweight=600,
                        transform=ax.transAxes)

            # Convert Piechart to PNG image
            plt.savefig(donut_to_IObytes, format='png', bbox_inches='tight')
            # Close a figure window
            plt.close()

            # Encode PNG image to base64 string
            return base64.b64encode(donut_to_IObytes.getvalue()).decode('utf-8')


# Create a histogram of imdb movie ratings
def imdb_histogram_pic():
    # Create a list to hold IMDB ratings
    IMDB_ratings = []
    # Append ratings to IMDB_ratings list
    for m in movie_list:
        IMDB_ratings.append(m.IMDB_rating)
    histogram_to_IObytes = io.BytesIO()
    # Set Title and labels for histogram
    plt.gca().set(title='IMDB Movie Ratings', ylabel='Number of Votes', xlabel='Ratings');
    # Create histogram
    plt.hist(IMDB_ratings, bins=10, color=['#F4E409'], edgecolor='#8F93A3')
    # Convert histogram as png file
    plt.savefig(histogram_to_IObytes, format='png', bbox_inches='tight')
    # Close a figure window
    plt.close()

    # Encode PNG image to base64 string
    return base64.b64encode(histogram_to_IObytes.getvalue()).decode('utf-8')


def metascore_histogram_pic():
    # Create a list to hold IMDB ratings
    metascore_ratings = []
    # Append ratings to IMDB_ratings list
    for m in movie_list:
        metascore_ratings.append(m.meta_score)
    histogram_to_IObytes = io.BytesIO()
    # Set Title and labels for histogram
    plt.gca().set(title='Metascore Rating', ylabel='Number of Votes', xlabel='Ratings');
    # Create histogram
    plt.hist(metascore_ratings, bins=10, color=['#9efd38'], edgecolor='#8F93A3')
    # Convert histogram as png file
    plt.savefig(histogram_to_IObytes, format='png', bbox_inches='tight')
    # Close a figure window
    plt.close()

    # Encode PNG image to base64 string
    return base64.b64encode(histogram_to_IObytes.getvalue()).decode('utf-8')


# Generates a list of movie title suggestions based on a movie title
def recommend(title):
    # Create a list for movies
    movie_list = []
    # Movie data to be used for k-means clustering
    movie_users = movie_data.pivot(index='Series_Title', columns='No_of_Votes', values='IMDB_Rating').fillna(0)

    movie_matrix = csr_matrix(movie_users.values)

    model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20)

    model_knn.fit(movie_matrix)

    NearestNeighbors(algorithm='brute', leaf_size=30, metric='cosine',
                     metric_params=None, n_jobs=None, n_neighbors=20, p=2,
                     radius=1.0)

    model_knn.fit(movie_matrix)

    # Retrieve movie index
    idx = process.extractOne(title, movie_data['Series_Title'])[2]

    distances, indices = model_knn.kneighbors(movie_matrix[idx], n_neighbors=40)

    # Generate movie list with string formating code
    for i in indices:
        movie_list.append(movie_data['Series_Title'][i].where(i != idx).dropna().to_string(index=False))
    # Return list with correct format
    x = movie_list[0].split('\n')

    return x


# Scores movie based on imdb rating
def score(rating):
    IMDB_rating = rating.IMDB_rating * 10

    if IMDB_rating >= 97.0:
        return 'A+'
    elif IMDB_rating >= 93.0:
        return 'A'
    elif IMDB_rating >= 90.0:
        return 'A-'
    elif IMDB_rating >= 87.0:
        return 'B+'
    elif IMDB_rating >= 83.0:
        return 'B'
    elif IMDB_rating >= 80.0:
        return 'B-'
    elif IMDB_rating >= 77.0:
        return 'C+'
    elif IMDB_rating >= 73.0:
        return 'C'
    elif IMDB_rating >= 70.0:
        return 'C-'
    elif IMDB_rating >= 67.0:
        return 'D'
    elif IMDB_rating > 0.0:
        return 'F'
    elif IMDB_rating == 0.0:
        return 'N/A'
    else:
        return 'Err'


# Scores movie based on metascore
def meta_score(score):
    meta_score = score.meta_score

    if meta_score >= 95.0:
        return 'A+'
    elif meta_score >= 93.0:
        return 'A'
    elif meta_score >= 91.0:
        return 'A-'
    elif meta_score >= 83.0:
        return 'B+'
    elif meta_score >= 75.0:
        return 'B'
    elif meta_score >= 67.0:
        return 'B-'
    elif meta_score >= 58.0:
        return 'C+'
    elif meta_score >= 50.0:
        return 'C'
    elif meta_score >= 42.0:
        return 'C-'
    elif meta_score >= 25.0:
        return 'D'
    elif meta_score >= 16.0:
        return 'D-'
    elif meta_score >= 8.0:
        return 'F'
    elif meta_score == 0.0:
        return 'N/A'
    else:
        return 'Err'


# Function that populates a list of the movie titles for auto-suggestions and to guard routes
def movie_titles():
    # Create a list to temporarily hold movie titles
    titles = []
    # Create a list to hold movie titles in the correct format
    titles_true = []

    # Append titles and remove index numbering
    for movie in movie_data:
        titles.append(movie_data['Series_Title'].to_string(index=False))

    # Create list and split long movie string
    titles = titles[0].split('\n')

    # Append titles in the correct format to titles_true
    for title in titles:
        titles_true.append(title.lstrip())

    return titles_true


# Generate movie objects from recommended list, used for generating cards
def m_info_list(title):
    # Create list to hold recommended titles
    m_list = recommend(title)
    # Create list to hold movies in correct format
    m_list_true = []
    # Create list to hold movie objects of recommnded titles
    recommend_list = []
    # Removes left padding
    for movie in m_list:
        m_list_true.append(movie.lstrip())

    # Append movie objects to list of recommended movies
    for movie in m_list_true:
        for x in load_data.movie_list:
            if movie == x.series_title:
                recommend_list.append(x)

    return recommend_list


# Function that populates a list of the movie titles for auto-suggestions
def movie_genres():
    # Create list to hold genre strings
    genres = []
    # Create list to hold correct genre strings in forrect format
    genre_list = []

    # Retrieve avaiable genres from movie_list data
    for movie in movie_list:
        genres.append(movie.genre.split())

    # Append genre in correct format to genre_list
    for list in genres:
        for genre in list:
            genre_list.append(genre.replace(',', ''))

    return genre_list
