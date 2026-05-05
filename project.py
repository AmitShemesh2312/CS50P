import requests
import os
from dotenv import load_dotenv
import sys
from ascii_magic import AsciiArt
from PIL import Image, ImageEnhance
import io
import argparse
import csv
import pyfiglet

load_dotenv()
api = os.getenv("TMDB_API_KEY")


def main():
    args = parse_arguments()

    if args.m:
        if args.m == "watchlist":
            print("Opening watchlist...")
            handle_list("Watchlist")
        elif args.m == "hearts":
            print("Opening hearts...")
            handle_list("Hearts")

        return

    # 2. Figure out the movie (or handle the list/flags)
    movie = get_movie(args)

    if not movie:
        return

    # 3. Fetch and draw the movie!
    response = get_movie_data(movie)
    top_movie = get_top_movie(response)
    poster_data = get_poster(top_movie)

    print(pyfiglet.figlet_format(top_movie["title"], font="Sub-Zero"))

    print("-" * 80)

    f = f"{top_movie['vote_average']} / 10"
    print(pyfiglet.figlet_format(f, font="small"))

    if poster_data:
        save_poster(poster_data)
        draw_poster(poster_data)

    # --- NEW ADDITION ---
    print("\nWould you like to save this movie?")
    print("[1] Add to Watchlist")
    print("[2] Add to Hearts")
    print("[Enter] Skip and exit")

    save_choice = input("> ").strip()

    if save_choice == "1":
        add_to_csv("watchlist.csv", top_movie["title"])
        print(f"Added '{top_movie['title']}' to your Watchlist!")
    elif save_choice == "2":
        add_to_csv("hearts.csv", top_movie["title"])
        print(f"Added '{top_movie['title']}' to your Hearts!")


def handle_list(list_name):
    movies = []
    filename = list_name.lower() + ".csv"

    # 1. Safely try to open the specific file passed in
    try:
        with open(filename, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                movies.append(row)
    except FileNotFoundError:
        # If the file doesn't exist yet, we just catch the error and do nothing!
        pass

    # 2. Check if the list is empty
    if not movies:
        print(f"\nYour {list_name} is currently empty!")
        return  # Stop the function right here

    # 3. Print the movies using the list_name in the header
    print(f"\n--- YOUR {list_name.upper()} ---")
    for index, movie in enumerate(movies):
        print(f"[{index + 1}] {movie['title']}")

    # 4. Ask the user what they want to do
    print("\nOptions: Type a number to remove a movie, or press Enter to go back.")
    choice = input("> ").strip()

    if choice.isdigit():
        index_to_remove = int(choice) - 1

        if 0 <= index_to_remove < len(movies):
            removed_movie = movies.pop(index_to_remove)
            print(f"Removed '{removed_movie['title']}' from your {list_name}.")
            # Save the updated list back to the correct file
            save_to_csv(filename, movies)
        else:
            print("Invalid number!")


def add_to_csv(filename, movie_title):
    """Appends a single movie to the specified CSV file."""

    # Check if the file already exists before we open it
    file_exists = os.path.isfile(filename)

    # Open in "a" (append) mode so we add to the bottom of the file
    with open(filename, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["title"])

        # If it is a brand new file, write the header first
        if not file_exists:
            writer.writeheader()

        # Write the new movie row
        writer.writerow({"title": movie_title})


def save_to_csv(filename, movies):
    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["title"])
        writer.writeheader()
        writer.writerows(movies)


def get_movie(args):

    if args.movie_words:
        return " ".join(args.movie_words)

    movie = input("What's your fav movie? ").strip()

    if not movie:
        print("You didn't enter a movie!")
        return None
    return movie


def parse_arguments():
    """Handles all command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m", choices=["watchlist", "hearts"], help="View your lists or hearts"
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
