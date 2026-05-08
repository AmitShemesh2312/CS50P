project.py
my project is searching movies and printing them nicely in the terminal.
after printing it asks the users if they wants to save them, they can choose to save the movie into 'watchlist' for movies they want to see or 'hearts' for movie that they liked
my project saves the poster to poster.jpg so users could see the differences.



users can type as command line argument a movie name or "-m" and a list like 'watchlist' or 'hearts':
"python project.py -m hearts"
"python project.py michael"

need TMDB account
need .env file and a key named TMDB_API_KEY

in the .env file : 
TMDB_API_KEY=...


the project needs to import:
pyfiglet
pillow
ascii_magic
dotenv
requests