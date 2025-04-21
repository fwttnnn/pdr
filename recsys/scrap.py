#!/usr/bin/env python

"""
A recursive Roblox game scraper based on user's fav list and it's friends.
"""

import time
import re
import requests
import emoji
from . import csv

CSV_GAMES_FILEPATH = "data/games.csv"
CSV_USERS_FILEPATH = "data/users.csv"

def user_get_friends(user_id: int) -> list[int]:
    resp = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/friends")
    data = resp.json()
    return [user_detail["id"] for user_detail in data["data"]]

def user_get_fav_games(user_id: int, _cursor: str = "") -> list[int]:
    resp = requests.get(f"https://www.roblox.com/users/favorites/list-json?assetTypeId=9&cursor={_cursor}&itemsPerPage=100&userId={user_id}")
    data = resp.json()
    games: list[int] = [game["Item"]["UniverseId"] for game in data["Data"]["Items"]]

    if data["Data"]["NextCursor"]:
        games.extend(user_get_fav_games(user_id, _cursor=data["Data"]["NextCursor"]))

    return games

def game_get_details(game_id: int, retries: int = 0) -> dict:
    resp = requests.get(f"https://games.roblox.com/v1/games?universeIds={game_id}")
    data = resp.json()

    # TODO: refactor
    if "errors" in data:
        if retries >= 3:
            retries = -1
            time.sleep(.5)

        return game_get_details(game_id, retries + 1)

    data: dict = data["data"][0]
    genres: list = [data["genre"], data["genre_l1"], data["genre_l2"]]

    return {
        "id":            data["id"],
        "rpid":          data["rootPlaceId"],
        "title":         emoji.replace_emoji(data["name"], r"").strip(),
        "description":   emoji.replace_emoji(re.sub(r"\r?\n", r"\\n", data["description"] or ""), r"").strip(),
        "genres":         "|".join(genres),
        "visits":        data["visits"],
        "favorite":      data["favoritedCount"],
        "created":       data["created"],
        "updated":       data["updated"],
    }

def csv_load_game_ids(path: str) -> set[int]:
    return csv.load_nth_row(path, 0)

def csv_load_user_ids(path: str) -> set[int]:
    return csv.load_nth_row(path, 0)
        
if __name__ == "__main__":
    csv.ensure_exist(CSV_USERS_FILEPATH)
    csv.ensure_exist(CSV_GAMES_FILEPATH)

    uid = 1531539874
    users = csv_load_user_ids(CSV_USERS_FILEPATH)
    games = csv_load_game_ids(CSV_GAMES_FILEPATH)

    (csv_fd_users, csv_writer_users) = csv.insert_headers(CSV_USERS_FILEPATH, ["id", "games", "friends"])
    (csv_fd_games, csv_writer_games) = csv.insert_headers(CSV_GAMES_FILEPATH, ["id", "rpid", "title", "description", "genres", "visits", "favorite", "created", "updated"])

    __user_games = user_get_fav_games(uid)
    __user_friends = user_get_friends(uid)

    for game_id in __user_games:
        if game_id in games:
            continue

        games.add(game_id)
        csv_writer_games.writerow(game_get_details(game_id))

    # TODO: this does not check for updated user games/friends
    if not (uid in users):
        csv_writer_users.writerow({"id": uid, "games": "|".join(map(str, __user_games)), "friends": "|".join(map(str, __user_friends))})

    csv_fd_games.close()
    csv_fd_users.close()
