import pytest
from project import check_command_args, get_movie, get_top_movie
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "-m", choices=["watchlist", "hearts"], help="View your watchlist or hearts"
)
parser.add_argument("movie_words", nargs="*", help="The name of the movie")
args = parser.parse_args(["pirates", "of", "the", "caribbean"])


def test_check_command_args():
    assert check_command_args(args) == False


def test_get_movie():
    assert get_movie(args) == "pirates of the caribbean"


def test_get_top_movie():
    mock_response = {
        "results": [
            {"title": "Pirates of the Caribbean", "id": 22},
            {"title": "Some Other Movie", "id": 99},
        ]
    }
    result = get_top_movie(mock_response)

    assert result["title"] == "Pirates of the Caribbean"
    assert result["id"] == 22
