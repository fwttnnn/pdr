#!/usr/bin/env python

"""
A recursive Roblox game scraper based on user's fav list and badges.

NOTE: scrapping badges requires Roblox authentication, set all necessary cookie in 'rcookie.json.example' 
      then rename it as 'rcookie.json'
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).absolute().parent.parent))

import time
import json
import re
import requests
import emoji
import recsys.csv

CSV_GAMES_FILEPATH = "data/games.csv"
CSV_USERS_FILEPATH = "data/users.csv"
__cookies: dict[str, str] = None

def __load_roblox_cookies() -> dict[str, str]:
    global __cookies
    if __cookies: return __cookies

    with open("rcookie.json", "r") as f:
        __cookies = json.load(f)

    return __cookies

def __roblox_api_get(url: str, cookies = None) -> dict:
    resp = requests.get(url, cookies=cookies).json()

    if "errors" in resp:
        time.sleep(.75)
        print(f"[ALERT!] Retrying.. {url}")
        return __roblox_api_get(url)
    
    return resp

def user_get_friends(user_id: int) -> list[int]:
    resp = __roblox_api_get(f"https://friends.roblox.com/v1/users/{user_id}/friends")
    return [user_detail["id"] for user_detail in resp["data"]]

def user_get_fav_games(user_id: int, _cursor: str = "") -> list[int]:
    resp = __roblox_api_get(f"https://www.roblox.com/users/favorites/list-json?assetTypeId=9&cursor={_cursor}&itemsPerPage=100&userId={user_id}")
    games: list[int] = [game["Item"]["UniverseId"] for game in resp["Data"]["Items"]]

    if resp["Data"]["NextCursor"]:
        games.extend(user_get_fav_games(user_id, _cursor=resp["Data"]["NextCursor"]))

    return games

def user_get_hist_games(user_id: int, _cursor: str = "") -> list[int]:
    resp = __roblox_api_get(f"https://badges.roblox.com/v1/users/{user_id}/badges?limit=100&sortOrder=Desc&cursor={_cursor}", cookies=__load_roblox_cookies())
    games: list[int] = list(set([badge["awarder"]["id"] for badge in resp["data"]]))

    if resp["nextPageCursor"]:
        games.extend(user_get_hist_games(user_id, _cursor=resp["nextPageCursor"]))

    return games

def game_convert_root_place_id(rpid: int) -> int:
    resp = __roblox_api_get(f"https://apis.roblox.com/universes/v1/places/{rpid}/universe")
    return resp["universeId"]

def game_get_details(game_ids: list[int]) -> list[dict]:
    N_GAMES_PER_CHUNK: int = 50
    chunks = [game_ids[i:i + N_GAMES_PER_CHUNK] for i in range(0, len(game_ids), N_GAMES_PER_CHUNK)]

    games = []
    for chunk in chunks:
        resp = __roblox_api_get(f"https://games.roblox.com/v1/games?universeIds={",".join(map(str, chunk))}")
        games.extend([{
            "id":            game["id"],
            "rpid":          game["rootPlaceId"],
            "title":         emoji.replace_emoji(game["name"], r"").strip(),
            "description":   emoji.replace_emoji(re.sub(r"\r?\n", r"\\n", game["description"] or ""), r"").strip(),
            "genres":        "|".join([game["genre"], game["genre_l1"], game["genre_l2"]]),
            "visits":        game["visits"],
            "favorite":      game["favoritedCount"],
            "created":       game["created"],
            "updated":       game["updated"],
        } for game in resp["data"]])

    return games

def csv_load_game_ids(path: str) -> set[int]:
    return recsys.csv.load_nth_row(path, 0)

def csv_load_root_game_ids(path: str) -> set[int]:
    return recsys.csv.load_nth_row(path, 1)

def csv_load_user_ids(path: str) -> set[int]:
    return recsys.csv.load_nth_row(path, 0)
        
if __name__ == "__main__":
    OPT_SCRAP_FROM_USER_BADGES = True

    recsys.csv.ensure_exist(CSV_USERS_FILEPATH)
    recsys.csv.ensure_exist(CSV_GAMES_FILEPATH)

    uid = 1531539874
    users = csv_load_user_ids(CSV_USERS_FILEPATH)
    games = csv_load_game_ids(CSV_GAMES_FILEPATH)
    rpids = csv_load_root_game_ids(CSV_GAMES_FILEPATH)

    (csv_fd_users, csv_writer_users) = recsys.csv.insert_headers(CSV_USERS_FILEPATH, ["id", "favorites", "history", "friends"])
    (csv_fd_games, csv_writer_games) = recsys.csv.insert_headers(CSV_GAMES_FILEPATH, ["id", "rpid", "title", "description", "genres", "visits", "favorite", "created", "updated"])

    __user_fav_games = user_get_fav_games(uid)
    __user_hist_games = []
    if OPT_SCRAP_FROM_USER_BADGES:
        __user_hist_games = [game_convert_root_place_id(rpid) for rpid in user_get_hist_games(uid) if rpid not in rpids or rpids.add(rpid)] 

    __user_friends = user_get_friends(uid)

    for game in game_get_details([id for id in __user_fav_games + __user_hist_games if id not in games or games.add(id)]):
        csv_writer_games.writerow(game)

    # TODO: this does not check for updated user games/friends
    if not (uid in users):
        csv_writer_users.writerow({"id":        uid, 
                                   "favorites": "|".join(map(str, __user_fav_games)), 
                                   "history":   "|".join(map(str, __user_hist_games)),
                                   "friends":   "|".join(map(str, __user_friends))})

    csv_fd_games.close()
    csv_fd_users.close()
