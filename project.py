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

# getting the .env key
load_dotenv()

# stroring the .env key in 'api' variable
api = os.getenv("TMDB_API_KEY")


def main():
    # getting command line argument as args
    args = parse_arguments()

    # checking if there is a command (-m)
    if check_command_args(args):

        # openning the list
        movie_list = show_list(args.m)

        # checking if user wants to remove a movie
        remove_movie(movie_list, args.m)
        return None

    # getting movie name as a string
    movie = get_movie(args)

    # if movie is blank, user didn't write a movie, exiting program
    if not movie:
        print("No movie specified")
        return None

    # get dict response for found movies
    response = get_movie_data(movie)

    try:
        # trying to get the top result out of the movies dict
        top_movie = get_top_movie(response)
    except NameError:
        print("no movies found with that name")
        return None

    # getting poster binary data if there is
    poster_data = get_poster(top_movie)

    # printing movie details
    display_movie(top_movie, poster_data)

    # if the user chose to save the movie
    save_movie = decision()

    # saves the movie
    add_choice_list(save_movie, top_movie)


def check_command_args(args) -> bool:
    # checking if user specify command

    modes = ["watchlist", "hearts"]
    return args.m in modes


def parse_arguments() -> argparse.Namespace:
    # checking if user specify movie or command
    # returning args object

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
    # saving the movie to the chosen list

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


def decision() -> str:
    # check if user want to save the movie

    print()
    print("Would you like to save this movie?")
    print("[1] Add to Watchlist")
    print("[2] Add to Hearts")
    print("[Enter] Skip and exit")

    return input("> ").strip()


def display_movie(movie, poster):
    # print movie details

    # print movie name
    print(pyfiglet.figlet_format(movie["title"], font="Sub-Zero", width=150))

    print("-" * 80)

    f = f"{movie['vote_average']:.1f} / 10"

    # printing movie rank
    print(pyfiglet.figlet_format(f, font="small"))

    if poster:
        # save poster to poster.jpg
        save_poster(poster)
        # print poster
        draw_poster(poster)


def show_list(list_name) -> list[dict] | None:
    # displaying the provided list
    file_name = list_name + ".csv"
    movies = []

    try:
        with open(file_name, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                movies.append(row)
    except FileNotFoundError:
        pass

    print()

    if not movies:
        print(f"{list_name} is currently empty!")
        return None

    else:
        print(f"--- YOUR {list_name.upper()} ---")
        for index, movie in enumerate(movies):
            print(f"[{index + 1}] {movie['title']}")

        return movies


def remove_movie(movie_list, file_name):
    # asks the user if he want to remove a movie from the list, and removes it
    file_name = file_name + ".csv"
    print()
    print("Options: Type a number to remove a movie, or press Enter to go back")
    choice = input("> ").strip()

    if choice.isdigit():
        index_to_remove = int(choice) - 1

        if 0 <= index_to_remove < len(movie_list):
            removed_movie = movie_list.pop(index_to_remove)
            print(f"Removed '{removed_movie['title']}' from {file_name}")

            save_to_csv(file_name, movie_list)
        else:
            print("Invalid number!")


def add_to_csv(filename, movie_title) -> bool:
    # adds the movie to the chosen csv and returning if movie added

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
    # saves the list of movies to the csv

    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["title"])
        writer.writeheader()
        writer.writerows(movies)


def get_movie(args) -> str | None:
    # getting movie name from command line arguments or user input
    if args.movie_words:
        return " ".join(args.movie_words)

    movie = input("What's your fav movie? ").strip()

    if not movie:
        return None
    return movie


def draw_poster(content):
    # draws the poster on the terminal from binary data, using io, pillow and ascii-art

    # transorming binary data to file like object - pillow needs a file to read, not a binary
    image_file = io.BytesIO(content)

    img = Image.open(image_file)

    # enhance the poster to make it more prominent
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)

    # making the image ascii-art object
    art = AsciiArt(img)

    # draw the image on the terminal
    art.to_terminal(columns=80)


def save_poster(content):
    # saves the poster to poster.jpg file (for comparing)
    filename = "poster.jpg"

    with open(filename, "wb") as file:
        file.write(content)


def get_poster(movie) -> bytes | None:
    # extracting the binary poster data if there is

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


def get_top_movie(response) -> dict:
    # from the dict of movies returns the top movie
    movies = response["results"]
    if not movies:
        raise NameError("movie not found!")
    return movies[0]


def get_movie_data(movie) -> dict:
    # getting response of movies that were found via TMDB API

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
