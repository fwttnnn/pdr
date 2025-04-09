#!/usr/bin/env python

"""
A recursive Roblox game scraper based on user's fav list and it's friends.
"""

import sys
import requests
import queue
from pprint import pprint

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

def game_get_details(game_id: int) -> dict:
    resp = requests.get(f"https://games.roblox.com/v1/games?universeIds={game_id}")
    data = resp.json()
    assert(len(data["data"]) >= 1)

    data: dict = data["data"][0]
    return {
        "id":            data["id"],
        "name":          data["name"],
        "description":   data["description"],
        "genre_general": data["genre"],
        "genre_level_1": data["genre_l1"],
        "genre_level_2": data["genre_l2"],
        "visits":        data["visits"],
        "favorite":      data["favoritedCount"],
        "created":       data["created"],
        "updated":       data["updated"],
    }

if __name__ == "__main__":
    users_ids = queue.Queue()
    users_ids.put(47091519)

    uid = users_ids.get()
    games = user_get_fav_games(uid)
    pprint(game_get_details(games[0]))

    sys.exit(0)
