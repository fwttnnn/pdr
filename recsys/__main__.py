#!/usr/bin/env python

"""
Recommender system for Roblox.
"""

if __name__ == "__main__":
    import recsys.model
    import recsys.dataset
    import recsys.csv

    CSV_GAMES_FILEPATH = "data/games.csv"
    CSV_USERS_FILEPATH = "data/users.csv"

    recsys.csv.ensure_exist(CSV_GAMES_FILEPATH)
    games = recsys.model.similar(2640407187, k=10)

    print(f"games similar to '{recsys.dataset.get(2640407187)["title"]}':")
    for game in games:
        print(game)
