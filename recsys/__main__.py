#!/usr/bin/env python

"""
Recommender system for Roblox.
"""

if __name__ == "__main__":
    import recsys.model
    import recsys.dataset
    import recsys.csv

    recsys.csv.ensure_exist(recsys.csv.CSV_GAMES_FILEPATH)
    recsys.csv.ensure_exist(recsys.csv.CSV_USERS_FILEPATH)

    game = recsys.dataset.random()
    game = recsys.dataset.get(5965327520)
    print(f"games similar to '{game["title"]}' ({game["id"]}):")
    for __game in recsys.model.similar(int(game["id"]), k=10):
        print(__game)
