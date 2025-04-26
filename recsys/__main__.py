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
    print(f"games similar to '{game["title"]}' (https://roblox.com/games/{game["rpid"]}):")
    for __game in recsys.model.similar(int(game["id"]), k=10):
        print(__game)
    
    print()

    user = recsys.dataset.user_get(3612359136)
    n = 5
    user_game_hist_len = len(user["history"])
    user_game_hist_input = user["history"][:user_game_hist_len - n]
    user_game_hist_rest = user["history"][user_game_hist_len - n:]

    print(f"games prediction for user '{user["id"]}':")
    predictions = recsys.model.predict(user_game_hist_input, k=10)
    for __game in predictions:
        print(__game)
    
    count = 0
    predictions = set([p[2] for p in predictions])
    for __game_id in user_game_hist_rest:
        if __game_id in predictions:
            count += 1

    print(f"{count} games was in the user's history")
