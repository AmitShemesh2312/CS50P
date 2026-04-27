import requests
import os
from dotenv import load_dotenv
import json
import sys

load_dotenv()
api = os.getenv("TMDB_API_KEY")

def main():
    url = "https://api.themoviedb.org/3/movie/top_rated"
    payload = {"api_key": api, "query": "pixels"}

    try:
        response = requests.get(url, payload)
        response.raise_for_status()
    except requests.HTTPError:
        print("Could not complete request!")
        sys.exit()
        
        
    o = response.json()
    for movie in o:
        print(movie)
    
    print("yeah!")
    print(o)




if __name__ == "__main__":
    main()