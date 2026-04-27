import requests
import os
from dotenv import load_dotenv
import json
import sys

load_dotenv()
api = os.getenv("TMDB_API_KEY")

def main():
    url = "https://api.themoviedb.org/3/search/movie?query=Jumanji"
    payload = {"api_key": api}

    try:
        response = requests.get(url, payload)
        response.raise_for_status()
    except requests.HTTPError:
        print("Could not complete request!")
        sys.exit()
        
    o = response.json()
    movies = o["results"]
    
    if movies:
        top_movie = movies[0]
        print(top_movie["title"])
        print(top_movie["vote_average"])


if __name__ == "__main__":
    main()