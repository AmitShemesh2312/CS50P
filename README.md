Movie Search & Save

Video Demo: https://youtu.be/v36mZ2aKVGk
GitHub Repository: https://github.com/AmitShemesh2312/CS50P

Description:
This project is a command-line tool for searching movies, viewing their details in the terminal, and saving them into lists. The user runs the program with a movie name as an argument, and the program queries TMDB API for matching titles, picks the most relevant result, and prints it in a way that is meant to feel native to the terminal: the movie title is rendered in large ASCII letters using pyfiglet with the "Sub-Zero" font, the rating out of ten is shown in a smaller ASCII font, and the movie poster is downloaded, contrast-enhanced with pillow, and rendered as ASCII art directly in the terminal using the ascii-magic library. The poster is also saved to disk as poster.jpg so that the user can compare the original image to the ASCII version side by side.
After a movie is displayed, the program asks the user whether they want to save it. There are two options: a Watchlist for movies the user wants to see in the future, and a Hearts list for movies the user has already seen and loved. The user can also press Enter to skip and exit. The two lists are stored as CSV files (watchlist.csv and hearts.csv) in the project root, so saved movies persist between runs. To view either list, the user runs the program with the -m flag — for example, python project.py -m hearts. From the list view, the user can type the number next to a movie to remove it from that list.

Files:
project.py — It contains the main function, total of 16 functions. parse_arguments builds the command-line interface using argparse with one optional flag (-m) and a positional movie-name argument, and validates that the user does not pass both at once. get_movie_data and get_top_movie handle the TMDB API call and pick the first matching result. get_poster, save_poster, and draw_poster handle downloading the poster, saving it to disk, and rendering it as ASCII art. display_movie formats and prints the movie details. add_to_csv, save_to_csv, show_list, and remove_movie handle the layer for the user's two lists. decision and add_choice_list handle the post-display "save this movie?" prompt.
test_project.py — Pytest tests for three of the custom functions: check_command_args (verifying the argument-mode detection), get_movie (verifying that command-line words are joined into a single movie title string), and get_top_movie (verifying that the first result is correctly selected from a mocked TMDB response). The mock response in test_get_top_movie lets the tests run without making a real network call.
requirements.txt — The pip-installable dependencies required to run the project: python-dotenv, requests, ascii-magic, pillow, and pyfiglet.
watchlist.csv and hearts.csv — Created and updated automatically by the program. Each is a single-column CSV with a title header row.
poster.jpg — Overwritten on each search with the most recently fetched poster image.
.env — Not committed to the repository (it is in .gitignore). The user has to create this file themselves and add TMDB_API_KEY=<their key> for the program to work.

Design Choices:
I chose to render movie posters as ASCII art rather than opening them in an image viewer because the program is meant to feel like a CLI tool, not a wrapper around a GUI.
I split the saved-movies feature into two separate lists - Watchlist and Hearts - instead of one flat "favorites" list, because the two have different meanings to me. The Watchlist is aspirational (movies I want to see), and the Hearts list are movies I have already seen and loved.
For storage I used CSV for convinience.
For the command-line interface I went with argparse and a single -m flag plus a positional movie_words argument.

Setup:
Create a free TMDB account and request an API key at https://www.themoviedb.org/settings/api
Create a .env file in the project root containing: TMDB_API_KEY=your_key_here
Install dependencies: pip install -r requirements.txt
Run the program: python project.py <movie name>

Usage:
Search for a movie
    python project.py inception
View a saved list:
    python project.py -m watchlist
    python project.py -m hearts