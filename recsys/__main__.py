#!/usr/bin/env python

"""
Recommender system for Roblox.
"""

def __test_similar_game_recommendation():
    game = recsys.dataset.game_get_random()
    print(f"games similar to '{game["title"]}' (https://roblox.com/games/{game["rpid"]}):")
    for __game in recsys.model.similar(int(game["id"]), k=10):
        print(__game)

def __test_user_history_prediction():
    user = recsys.dataset.user_get(3612359136)
    hist = list(reversed(user["history"]))

    n = 10
    hist_len = len(hist)

    # hist_input = hist[:hist_len - n]
    # hist_rest = hist[hist_len - n:]

    hist_input = hist[:300]
    hist_rest = hist[300:]

    for i, game_id in enumerate(hist):
        game = recsys.dataset.game_get(game_id)
        print(f"{i + 1}: {game["title"]} (https://roblox.com/games/{game["rpid"]})")

    print(f"{hist_len} total games")
    print()

    count = 0
    hist_rest = set(hist_rest)

    print(f"games prediction for user '{user["id"]}':")
    predictions = recsys.model.predict(hist_input, k=10)
    for __game in predictions:
        print(__game, __game[2] in hist_rest)

        if __game[2] in hist_rest:
            count += 1

    print(f"{count} games was in the user's history")

if __name__ == "__main__":
    import recsys.model
    import recsys.dataset
    import recsys.csv

    recsys.csv.ensure_exist(recsys.csv.CSV_GAMES_FILEPATH)
    recsys.csv.ensure_exist(recsys.csv.CSV_USERS_FILEPATH)

    # __test_similar_game_recommendation()
    # print()

    __test_user_history_prediction()
