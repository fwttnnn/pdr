#!/usr/bin/env python

"""
Recommender system for Roblox.
"""

if __name__ == "__main__":
    import recsys.model
    import recsys.csv

    CSV_GAMES_FILEPATH = "data/games.csv"
    CSV_USERS_FILEPATH = "data/users.csv"

    recsys.csv.ensure_exist(CSV_GAMES_FILEPATH)
    games = recsys.csv.load(CSV_GAMES_FILEPATH)

    nth = 767-2

    print(f"games similar to '{games[nth]["title"]}':")
    for game in recsys.model.similar(games, nth, 10):
        print(game)
