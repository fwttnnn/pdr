#!/usr/bin/env python

"""
A recursive Roblox game scraper based on user's fav list and badges.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).absolute().parent.parent))

import time
import re
import requests
import emoji
import recsys.csv

CSV_GAMES_FILEPATH = "data/games.csv"
CSV_USERS_FILEPATH = "data/users.csv"

def user_get_friends(user_id: int) -> list[int]:
    resp = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/friends").json()
    return [user_detail["id"] for user_detail in resp["data"]]

def user_get_fav_games(user_id: int, _cursor: str = "") -> list[int]:
    resp = requests.get(f"https://www.roblox.com/users/favorites/list-json?assetTypeId=9&cursor={_cursor}&itemsPerPage=100&userId={user_id}").json()
    games: list[int] = [game["Item"]["UniverseId"] for game in resp["Data"]["Items"]]

    if resp["Data"]["NextCursor"]:
        games.extend(user_get_fav_games(user_id, _cursor=resp["Data"]["NextCursor"]))

    return games

def user_get_hist_games(user_id: int, _cursor: str = "") -> list[int]:
    resp = requests.get(f"https://badges.roblox.com/v1/users/{user_id}/badges?limit=100&sortOrder=Desc&cursor={_cursor}").json()
    games: list[int] = list(set([badge["awarder"]["id"] for badge in resp["data"]]))

    if resp["nextPageCursor"]:
        games.extend(user_get_hist_games(user_id, _cursor=resp["nextPageCursor"]))

    return games

def game_get_details(game_id: int, retries: int = 0) -> dict:
    resp = requests.get(f"https://games.roblox.com/v1/games?universeIds={game_id}").json()

    # TODO: refactor
    if "errors" in resp:
        if retries >= 3:
            retries = -1
            time.sleep(.5)

        return game_get_details(game_id, retries + 1)

    detail: dict = resp["data"][0]
    genres: list = [detail["genre"], detail["genre_l1"], detail["genre_l2"]]

    return {
        "id":            detail["id"],
        "rpid":          detail["rootPlaceId"],
        "title":         emoji.replace_emoji(detail["name"], r"").strip(),
        "description":   emoji.replace_emoji(re.sub(r"\r?\n", r"\\n", detail["description"] or ""), r"").strip(),
        "genres":         "|".join(genres),
        "visits":        detail["visits"],
        "favorite":      detail["favoritedCount"],
        "created":       detail["created"],
        "updated":       detail["updated"],
    }

def csv_load_game_ids(path: str) -> set[int]:
    return recsys.csv.load_nth_row(path, 0)

def csv_load_user_ids(path: str) -> set[int]:
    return recsys.csv.load_nth_row(path, 0)
        
if __name__ == "__main__":
    recsys.csv.ensure_exist(CSV_USERS_FILEPATH)
    recsys.csv.ensure_exist(CSV_GAMES_FILEPATH)

    uid = 1531539874
    users = csv_load_user_ids(CSV_USERS_FILEPATH)
    games = csv_load_game_ids(CSV_GAMES_FILEPATH)

    (csv_fd_users, csv_writer_users) = recsys.csv.insert_headers(CSV_USERS_FILEPATH, ["id", "favorites", "history", "friends"])
    (csv_fd_games, csv_writer_games) = recsys.csv.insert_headers(CSV_GAMES_FILEPATH, ["id", "rpid", "title", "description", "genres", "visits", "favorite", "created", "updated"])

    __user_fav_games = user_get_fav_games(uid)
    __user_hist_games = user_get_hist_games(uid)

    __user_games = __user_fav_games + __user_hist_games
    __user_friends = user_get_friends(uid)

    for game_id in __user_games:
        if game_id in games:
            continue

        games.add(game_id)
        csv_writer_games.writerow(game_get_details(game_id))

    # TODO: this does not check for updated user games/friends
    if not (uid in users):
        csv_writer_users.writerow({"id":        uid, 
                                   "favorites": "|".join(map(str, __user_fav_games)), 
                                   "history":   "|".join(map(str, __user_hist_games)),
                                   "friends":   "|".join(map(str, __user_friends))})

    csv_fd_games.close()
    csv_fd_users.close()
