#!/usr/bin/env python

"""
Recommender system for Roblox.
"""

if __name__ == "__main__":
    import recsys.dataset
    import recsys.model

    game = recsys.dataset.game_get_random()
    print(f"games similar to '{game["title"]}' (https://roblox.com/games/{game["rpid"]}):")
    for __game in recsys.model.similar(int(game["id"]), k=10):
        print(__game)
