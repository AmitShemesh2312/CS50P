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
    # getting command line argument as args
    args = parse_arguments()

    if check_args(args):
        return

    movie = get_movie(args)

    if not movie:
        print("No movie specified")
        return

    response = get_movie_data(movie)
    top_movie = get_top_movie(response)
    poster_data = get_poster(top_movie)

    display_movie(top_movie, poster_data)

    user_choice = decision()

    add_choice_list(user_choice, top_movie)


def check_args(args):
    if args.m:
        if args.m == "watchlist":
            print("Opening watchlist...")
            handle_list("Watchlist")
        elif args.m == "hearts":
            print("Opening hearts...")
            handle_list("Hearts")
        return True
    return False


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m", choices=["watchlist", "hearts"], help="View your watchlist or hearts"
    )
    parser.add_argument("movie_words", nargs="*", help="The name of the movie")
    args = parser.parse_args()

    if args.m and args.movie_words:
        parser.error("You cannot search for a movie and view a list at the same time!")

    return args


def add_choice_list(choice, movie):
    if choice == "1":
        if add_to_csv("watchlist.csv", movie["title"]):
            print(f"Added '{movie['title']}' to your Watchlist!")
        else:
            print(f"'{movie["title"]}' is already in your Watchlist!")
    elif choice == "2":
        if add_to_csv("hearts.csv", movie["title"]):
            print(f"Added '{movie['title']}' to your Hearts!")
        else:
            print(f"'{movie["title"]}' is already in your Hearts!")


def decision():
    print()
    print("Would you like to save this movie?")
    print("[1] Add to Watchlist")
    print("[2] Add to Hearts")
    print("[Enter] Skip and exit")

    return input("> ").strip()


def display_movie(movie, poster):
    # print movie
    print(pyfiglet.figlet_format(movie["title"], font="Sub-Zero", width=150))

    print("-" * 80)

    f = f"{movie['vote_average']:.1f} / 10"
    print(pyfiglet.figlet_format(f, font="small"))

    if poster:
        save_poster(poster)
        draw_poster(poster)


def handle_list(list_name):
    movies = []
    filename = list_name.lower() + ".csv"

    try:
        with open(filename, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                movies.append(row)
    except FileNotFoundError:
        pass

    if not movies:
        print()
        print(f"Your {list_name} is currently empty!")
        return

    print()
    print(f"--- YOUR {list_name.upper()} ---")
    for index, movie in enumerate(movies):
        print(f"[{index + 1}] {movie['title']}")

    print()
    print("Options: Type a number to remove a movie, or press Enter to go back")
    choice = input("> ").strip()

    if choice.isdigit():
        index_to_remove = int(choice) - 1

        if 0 <= index_to_remove < len(movies):
            removed_movie = movies.pop(index_to_remove)
            print(f"Removed '{removed_movie['title']}' from your {list_name}.")

            save_to_csv(filename, movies)
        else:
            print("Invalid number!")


def add_to_csv(filename, movie_title) -> bool:

    if os.path.isfile(filename):
        with open(filename, "r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:

                # returning false if movie in list
                if row["title"].lower() == movie_title.lower():
                    print()
                    return False

    file_exists = os.path.isfile(filename)

    with open(filename, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["title"])

        if not file_exists:
            writer.writeheader()

        writer.writerow({"title": movie_title})
    return True


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
        return None
    return movie


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
