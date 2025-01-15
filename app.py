from flask import Flask, render_template, request, redirect, url_for, flash
from extensions import db
from datamanager.sqlite_data_manager import SQLiteDataManager
from models import User, Movie
import logging
import requests

OMDB_API_KEY = '7a9062b5'

app = Flask(__name__, instance_relative_config=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.instance_path + '/moviweb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

data_manager = SQLiteDataManager(app)

app.logger.setLevel(logging.ERROR)

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    """Render the home page."""
    return render_template('home.html')


@app.route('/users')
def list_users():
    """List all users."""
    try:
        all_users = data_manager.get_all_users()
    except Exception as e:
        app.logger.error(f"Error fetching users: {str(e)}")
        return render_template('500.html'), 500
    return render_template('users.html', users=all_users)


@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    """Add a new user."""
    if request.method == 'POST':
        name = request.form['name']
        try:
            data_manager.add_user(name)
        except Exception as e:
            app.logger.error(f"Error adding user: {str(e)}")
            return render_template('500.html'), 500
        return redirect(url_for('list_users'))
    return render_template('add_user.html')


@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Delete a user."""
    try:
        data_manager.delete_user(user_id)
    except Exception as e:
        app.logger.error(f"Error deleting user {user_id}: {str(e)}")
        return render_template('500.html'), 500
    return redirect(url_for('list_users'))


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    """Display all movies for a user."""
    try:
        user = data_manager.get_user(user_id)
        if user is None:
            return render_template('404.html'), 404
        movies = data_manager.get_user_movies(user_id)
    except Exception as e:
        app.logger.error(f"Error fetching user movies for user_id {user_id}: {str(e)}")
        return render_template('500.html'), 500
    return render_template('user_movies.html', user=user, movies=movies)


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """Add a new movie to the user's movie list."""
    if request.method == 'POST':
        title = request.form['title']
        director = request.form['director']
        year = request.form['year']
        rating = request.form['rating']

        if title:
            omdb_url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
            response = requests.get(omdb_url)
            data = response.json()

            if data.get('Response') == 'True':
                director = data.get('Director', director)
                if director:
                    director = director.split(',')[0]

                title = data.get('Title', title)
                year = data.get('Year', year)
                rating = data.get('imdbRating', rating)

            else:
                flash(f"Movie '{title}' not found in OMDb. Please manually enter the details.", "warning")

        new_movie = Movie(
            title=title,
            director=director,
            year=year,
            rating=rating,
            user_id=user_id
        )

        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('user_movies', user_id=user_id))

    return render_template('add_movie.html', user_id=user_id)


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """Update an existing movie for a user."""
    movie = Movie.query.get(movie_id)
    if not movie:
        return "Movie not found", 404

    if request.method == 'POST':
        title = request.form['title']
        rating = request.form['rating']
        year = request.form['year']
        director = request.form['director']

        if not title or len(title) > 100:
            return "Invalid title. Title cannot be empty.", 400

        if not director.replace(" ", "").isalpha():
            return "Invalid director name. Only letters and spaces are allowed.", 400

        try:
            rating = float(rating)
            year = int(year)

            if rating < 1 or rating > 10:
                return "Rating must be between 1 and 10.", 400

            movie.title = title
            movie.rating = rating
            movie.year = year
            movie.director = director

            db.session.commit()
            return redirect(url_for('view_movie', user_id=user_id, movie_id=movie.id))

        except ValueError as e:
            return f"Error: {e}", 500

    return render_template('update_movie.html', user_id=user_id, movie=movie)


@app.route('/users/<int:user_id>/view_movie/<int:movie_id>')
def view_movie(user_id, movie_id):
    """View a single movie details."""
    user = User.query.get(user_id)
    movie = Movie.query.get(movie_id)

    if not user or not movie:
        return f"User or Movie not found (user_id: {user_id}, movie_id: {movie_id})", 404

    return render_template('view_movie.html', user=user, movie=movie, user_id=user_id)


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(user_id, movie_id):
    """Delete a movie for a user."""
    try:
        data_manager.delete_movie(movie_id)
    except Exception as e:
        app.logger.error(f"Error deleting movie {movie_id}: {str(e)}")
        return render_template('500.html'), 500
    return redirect(url_for('user_movies', user_id=user_id))


@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors."""
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)
