#!/usr/bin/env python

"""
Recommender system for Roblox.
"""

if __name__ == "__main__":
    import recsys
    import re
    from . import csv

    CSV_GAMES_FILEPATH = "data/games.csv"
    CSV_USERS_FILEPATH = "data/users.csv"

    csv.ensure_exist(CSV_GAMES_FILEPATH)
    games = csv.load(CSV_GAMES_FILEPATH)

    nth = 715-2

    print(f"games similar to '{games[nth]["title"]}':")
    for game in recsys.similar(games, nth, 10):
        print(game)
