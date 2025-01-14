import requests

OMDB_API_KEY = '7a9062b5'


def get_movie_details(title):
    """
    Fetches movie details from the OMDb API based on the provided title.

    Args:
        title (str): The title of the movie for which details are being fetched.

    Returns:
        dict: A dictionary containing movie details such as title, year, rating, etc.
              If the movie is not found, or if there is an error with the API request,
              it returns a dictionary with an error message.
    """
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"

    try:
        response = requests.get(url)
        movie_data = response.json()

        if response.status_code == 200:
            if movie_data.get('Error'):
                return {"Error": movie_data['Error']}

            return {
                'Title': movie_data.get('Title', 'N/A'),
                'Year': movie_data.get('Year', 'N/A'),
                'imdbRating': movie_data.get('imdbRating', 'N/A'),
                'Poster': movie_data.get('Poster', 'N/A'),
                'Plot': movie_data.get('Plot', 'No plot available')  # Default for missing plot
            }
        else:
            return {"Error": "Movie not found"}

    except requests.exceptions.RequestException as e:
        return {"Error": f"API connection error: {e}"}