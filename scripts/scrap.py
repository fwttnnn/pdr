#!/usr/bin/env python

"""
A recursive Roblox game scraper based on user's fav list and it's friends.
"""

import sys
import time
import re
import io
import os
import requests
import queue
import csv
from pprint import pprint

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
        "name":          data["name"],
        "description":   re.sub(r"\r?\n", r"\\n", data["description"] or ""),
        "genres":         "|".join(genres),
        "visits":        data["visits"],
        "favorite":      data["favoritedCount"],
        "created":       data["created"],
        "updated":       data["updated"],
    }
        
def csv_load_nth_row(path: str, nth: int) -> set[int]:
    with open(path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)

        ids = [row[nth] for row in reader]
        if len(ids) >= 1:
            ids.pop(0)

        return set(map(int, ids))

    return set()

def csv_insert_headers(path: str, headers: list[str]) -> tuple[io.TextIOWrapper, csv.DictWriter]:
    f = open(path, mode="a", newline="", encoding="utf-8")
    w = csv.DictWriter(f, fieldnames=headers)

    if os.stat(path).st_size == 0:
        w.writeheader()

    return f, w

def csv_load_game_ids(path: str = CSV_GAMES_FILEPATH) -> set[int]:
    return csv_load_nth_row(path, 0)

def csv_load_user_ids(path: str = CSV_USERS_FILEPATH) -> set[int]:
    return csv_load_nth_row(path, 0)

def csv_ensure_exist(path: str) -> None:
    if not os.path.exists(path):
        open(path, "w").close()

if __name__ == "__main__":
    csv_ensure_exist(CSV_USERS_FILEPATH)
    csv_ensure_exist(CSV_GAMES_FILEPATH)

    uid = 1531539874
    users = csv_load_user_ids()
    games = csv_load_game_ids()

    (csv_fd_users, csv_writer_users) = csv_insert_headers(CSV_USERS_FILEPATH, ["id", "games", "friends"])
    (csv_fd_games, csv_writer_games) = csv_insert_headers(CSV_GAMES_FILEPATH, ["id", "name", "description", "genres", "visits", "favorite", "created", "updated"])

    __user_games = user_get_fav_games(uid)
    __user_friends = user_get_friends(uid)

    for game_id in __user_games:
        if game_id in games:
            continue

        games.add(game_id)
        csv_writer_games.writerow(game_get_details(game_id))

    if not (uid in users):
        csv_writer_users.writerow({"id": uid, "games": "|".join(map(str, __user_games)), "friends": "|".join(map(str, __user_friends))})

    csv_fd_games.close()
    csv_fd_users.close()
    sys.exit(0)
