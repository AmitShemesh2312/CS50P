import requests
import os
from dotenv import load_dotenv
import sys
from ascii_magic import AsciiArt
from PIL import Image, ImageEnhance
import io
import argparse
import csv

load_dotenv()
api = os.getenv("TMDB_API_KEY")


def main():
    # 1. Parse arguments
    args = parse_arguments()

    if args.m:
        if args.m == "watchlist":
            print("Opening watchlist...")
            open_watchlist()
        elif args.m == "bookmarks":
            print("Opening bookmarks...")
            open_bookmarks()

        return  # Stop main() right here. We are done!

    # 2. Figure out the movie (or handle the list/flags)
    movie = get_movie(args)

    if not movie:
        return

    # 3. Fetch and draw the movie!
    response = get_movie_data(movie)
    top_movie = get_top_movie(response)
    poster_data = get_poster(top_movie)

    if poster_data:
        save_poster(poster_data)
        draw_poster(poster_data)

    print(top_movie["title"])
    print(f"{top_movie['vote_average']} / 10")


def open_bookmarks(): ...


def open_watchlist(): ...


def get_movie(args):
    """Handles the list flags or gets the movie title from the user."""
    # 2. Check if they typed a movie in the command line

    if args.movie_words:
        movie = " ".join(args.movie_words)

    # 3. Fall back to asking them with input()
    else:
        movie = input("What's your fav movie? ").strip()

    # Catch empty inputs
    if not movie:
        print("You didn't enter a movie!")
        return None

    # If we made it this far, return the actual movie string!
    return movie


def parse_arguments():
    """Handles all command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m", choices=["watchlist", "bookmarks"], help="View your lists or bookmarks"
    )
    parser.add_argument(
        "movie_words", nargs="*", help="The name of the movie to search for"
    )
    args = parser.parse_args()

    # Guardrail
    if args.m and args.movie_words:
        parser.error("You cannot search for a movie and view a list at the same time!")

    return args


def draw_poster(content):
    image_file = io.BytesIO(content)
    img = Image.open(image_file)

    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)

    art = AsciiArt(img)
    art.to_terminal(columns=80)


def save_poster(content):
    filename = "poster.jpg"

    with open(filename, "wb") as file:
        file.write(content)

    print(f"Poster successfully saved")


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
