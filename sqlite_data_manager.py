from extensions import db
from models import User, Movie
from data_manager_interface import DataManagerInterface


class SQLiteDataManager(DataManagerInterface):
    def __init__(self, app, db_file_name='moviweb.db'):
        """Initialize SQLiteDataManager with Flask app and database file."""
        self.app = app
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_file_name}"
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    def _get_session(self):
        """Get a session with app context."""
        return self.app.app_context()

    def get_all_users(self):
        """Fetch all users from the database."""
        with self._get_session():
            return db.session.query(User).all()

    def get_user(self, user_id):
        """Fetch a specific user by user_id."""
        with self._get_session():
            return db.session.query(User).get(user_id)

    def get_user_movies(self, user_id):
        """Fetch all movies for a specific user."""
        with self._get_session():
            return db.session.query(Movie).filter(Movie.user_id == user_id).all()

    def get_movie(self, movie_id):
        """Fetch a specific movie by movie_id."""
        with self._get_session():
            return db.session.query(Movie).get(movie_id)

    def add_user(self, name):
        """Add a new user to the database."""
        with self._get_session():
            new_user = User(name=name)
            db.session.add(new_user)
            db.session.commit()

    @staticmethod
    def delete_user(user_id):
        """Delete a user from the database."""
        try:
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
        except Exception as e:
            raise Exception(f"Error deleting user {user_id}: {str(e)}")

    def add_movie(self, user_id, title, director, year, rating):
        """Add a new movie to the database."""
        with self._get_session():
            new_movie = Movie(title=title, director=director, year=year, rating=rating, user_id=user_id)
            db.session.add(new_movie)
            db.session.commit()

    def update_movie(self, movie_id, title=None, director=None, year=None, rating=None):
        """Update a movie's details."""
        with self._get_session():
            movie = db.session.query(Movie).get(movie_id)
            if movie:
                if title:
                    movie.title = title
                if director:
                    movie.director = director
                if year:
                    movie.year = year
                if rating:
                    movie.rating = rating
                db.session.commit()

    def delete_movie(self, movie_id):
        """Delete a movie from the database."""
        with self._get_session():
            movie = db.session.query(Movie).get(movie_id)
            if movie:
                db.session.delete(movie)
                db.session.commit()