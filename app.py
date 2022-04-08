from flask import Flask, render_template, request, redirect, url_for, flash
import functions
import load_data
from load_data import *

app = Flask(__name__)

# Secret key to secure user inputs, used for flash messages
app.secret_key = 'the_random_string'

# App route
@app.route('/', methods=["POST", "GET"])
def index():
    # Function to render histogram of movie ratings
    imdb_to_IObytes = functions.imdb_histogram_pic()
    metascore_to_IObytes = functions.metascore_histogram_pic()
    # Retrieving query value
    query = request.args.get('query')
    # Titles for auto-suggestion
    titles = functions.movie_titles()

    # Passes query to list.html

    # During submission
    if request.method == "POST":

        # Returns user query from form
        query = request.form['query']

        # Loops and test query against availble movie titles
        while query not in titles:
            flash('Movie not found please try again')
            return redirect(url_for('index'))

        # Render page and pass information
        return redirect(url_for('list', query=query))
    else:
        # Render page and pass information
        return render_template('index.html', imdb_image="data:image/png;base64," + imdb_to_IObytes, metascore_image="data:image/png;base64," + metascore_to_IObytes, titles=titles)


# Query route
@app.route('/<query>')
def list(query):
    # Titles to check if it exists
    titles = functions.movie_titles()

    # If query does not exist redirect and present flash message
    while query not in titles:
        flash('Movie not found please try again')
        return redirect(url_for('index'))

    # Function to render cluster
    cluster_to_IObytes = functions.cluster_pic()
    # Returns movie list recommendations based on query
    movies_list = functions.recommend(query)
    # Contains list of movies and details
    m_list = functions.m_info_list(query)
    # Contains list of genres
    genre_list = load_data.genre_data

    # Render page and pass information
    return render_template('list.html', query=query, m_list=m_list, movies_list=movies_list, genre_list=genre_list, image="data:image/png;base64," + cluster_to_IObytes)

# Movie route
@app.route('/m/<title>')
def movie(title):
    # Titles to check if it exists
    titles = functions.movie_titles()

    # Loops and test title against availble movie titles
    while title not in titles:
        # Flash Message
        flash('Movie not found please try again')
        # Redirect to index
        return redirect(url_for('index'))

    # Searches title for a match in movie list
    for m in movie_list:
        # Loop and returns title match
        if m.series_title == title:

            # Donut Chart for imdb and metascore
            imdb_donut_to_IObytes = functions.pie_pic(title, 'imdb')
            meta_donut_to_IObytes = functions.pie_pic(title, 'meta')

            # Render movie page and pass movie information
            return render_template('movie.html', title=m.series_title, year=m.released_year, runtime=m.runtime,
                                   genre=m.genre, imdb=m.IMDB_rating, overview=m.overview, meta=m.meta_score,
                                   director=m.director, star1=m.star1, star2=m.star2, star3=m.star3, star4=m.star4,
                                   imdb_pie_image="data:image/png;base64," + imdb_donut_to_IObytes,
                                   meta_pie_image="data:image/png;base64," + meta_donut_to_IObytes
                                   )
# 404 not found route
@app.errorhandler(404)
def handle_404(e):
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
