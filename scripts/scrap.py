#!/usr/bin/env python

"""
A recursive Roblox game scraper based on user's fav list and it's friends.
"""

import sys
import time
import re
import os
import requests
import queue
import csv
from pprint import pprint

CSV_FILEPATH = "data/games.csv"

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
    return {
        "id":            data["id"],
        "name":          data["name"],
        "description":   re.sub(r"\r?\n", r"\\n", data["description"]),
        "genre_general": data["genre"],
        "genre_level_1": data["genre_l1"],
        "genre_level_2": data["genre_l2"],
        "visits":        data["visits"],
        "favorite":      data["favoritedCount"],
        "created":       data["created"],
        "updated":       data["updated"],
    }
        
def csv_load_game_ids(path: str = CSV_FILEPATH) -> set[int]:
    with open(path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)

        ids = [row[0] for row in reader]
        if len(ids) >= 1:
            ids.pop(0)

        return set(map(int, ids))

    return set()

if __name__ == "__main__":
    users_ids = queue.Queue()
    users_ids.put(47091519)

    games = csv_load_game_ids()
    f = open(CSV_FILEPATH, mode="a", newline="", encoding="utf-8")
    w = csv.DictWriter(f, fieldnames=["id", "name", "description", "genre_general", "genre_level_1", "genre_level_2", "visits", "favorite", "created", "updated"])

    if os.stat(CSV_FILEPATH).st_size == 0:
        w.writeheader()

    uid = users_ids.get()
    for game_id in user_get_fav_games(uid):
        if game_id in games:
            continue

        games.add(game_id)
        w.writerow(game_get_details(game_id))

    f.close()
    sys.exit(0)
