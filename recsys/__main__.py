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

    game = recsys.dataset.game_get_random()
    print(f"games similar to '{game["title"]}' ({game["id"]}):")
    for __game in recsys.model.similar(int(game["id"]), k=10):
        print(__game)
