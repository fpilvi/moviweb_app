import pytest
from app import app, db
from models import User, Movie


@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/test_moviweb.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_add_user(client):
    """Test adding a user."""
    response = client.post('/users/add', data={'name': 'Johnny Ponny'})
    assert response.status_code == 302
    assert User.query.count() == 1
    user = User.query.first()
    assert user.name == 'Johnny Ponny'


def test_add_movie(client):
    """Test adding a movie."""
    with app.app_context():
        user = User(name='Johnny Ponny')
        db.session.add(user)
        db.session.commit()

    response = client.post('/users/1/add_movie', data={
        'title': 'Inception',
        'director': 'Christopher Nolan',
        'year': 2010,
        'rating': 8.8
    })
    assert response.status_code == 302
    assert Movie.query.count() == 1
    movie = Movie.query.first()
    assert movie.title == 'Inception'
    assert movie.director == 'Christopher Nolan'


def test_get_user_movies(client):
    """Test retrieving a user's movies."""
    with app.app_context():
        user = User(name='Johnny Ponny')
        db.session.add(user)
        db.session.commit()
        movie = Movie(
            title='Inception',
            director='Christopher Nolan',
            year=2010,
            rating=8.8,
            user_id=user.id
        )
        db.session.add(movie)
        db.session.commit()

    response = client.get('/users/1')
    assert response.status_code == 200
    assert b'Inception' in response.data


def test_delete_user(client):
    """Test deleting a user."""
    with app.app_context():
        user = User(name='Johnny Ponny')
        db.session.add(user)
        db.session.commit()

    response = client.post('/users/1/delete')
    assert response.status_code == 302
    assert User.query.count() == 0


def test_delete_movie(client):
    """Test deleting a movie."""
    with app.app_context():
        user = User(name='Johnny Ponny')
        db.session.add(user)
        db.session.commit()
        movie = Movie(
            title='Inception',
            director='Christopher Nolan',
            year=2010,
            rating=8.8,
            user_id=user.id
        )
        db.session.add(movie)
        db.session.commit()

    response = client.post('/users/1/delete_movie/1')
    assert response.status_code == 302
    assert Movie.query.count() == 0
