import requests
import os
from dotenv import load_dotenv
import sys

load_dotenv()
api = os.getenv("TMDB_API_KEY")

def main():
    #movie = input("What's you fav movie? ").strip()
    movie = "back to the future"
    response = get_movie_data(movie)
    
    top_movie = get_top_movie(response)
    
    poster_data = get_poster(top_movie)
    
    if poster_data:
        save_poster(poster_data)
    
    print(top_movie["title"])
    print(top_movie["vote_average"])
    
    
def save_poster(content):
    filename = "poster.jpg"
    
    if not content:
        print("No content to save.")
        return
    
    # Open a file in 'write binary' mode
    with open(filename, "wb") as file:
        file.write(content)
    
    print(f"Poster successfully saved as {filename}")
    
    
def get_poster(movie):
    poster_url = "https://image.tmdb.org/t/p/"
    path = movie.get("poster_path")
    
    if not path:
        print("This movie doesn't have a poster!")
        return None
    
    size = "w500"
    
    full_url = f"{poster_url}{size}{path}"
    
    response = requests.get(full_url)
    
    if response.status_code == 200:
        return response.content
    else:
        print("Failed to download image")
        return None
    
    
    
def get_top_movie(response):
    movies = response["results"]
    if not movies:
        raise NameError("movie not found!")
    return movies[0]

        
def get_movie_data(movie):
    # gets movie name and returns ...
    
    url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": api, "query": movie}
    
    try:
        response = requests.get(url, params)
        response.raise_for_status()
    except requests.HTTPError:
        print("Could not complete request!")
        sys.exit()
        
    return response.json()


if __name__ == "__main__":
    main()