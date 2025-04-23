#!/usr/bin/env python

"""
Recommender system for Roblox.
"""

if __name__ == "__main__":
    import recsys.model
    import recsys.dataset
    import recsys.csv

    recsys.csv.ensure_exist(recsys.csv.CSV_GAMES_FILEPATH)

    games = recsys.model.similar(2640407187, k=10)
    print(f"games similar to '{recsys.dataset.get(2640407187)["title"]}':")
    for game in games:
        print(game)

    print()

    __hist = [2640407187, 371263894, 2865328349, 3089546450, 7197190464, 2360092394]
    games = recsys.model.predict(__hist[:3], k=10)
    print(f"next game predictions:")
    for game in games:
        print(game)
