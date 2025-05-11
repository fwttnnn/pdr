#!/usr/bin/env python

"""
Roblox game scraper based on user's fav list and badges.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).absolute().parent.parent.joinpath("lib")))

import time
import random
import threading
import re
import requests
import emoji
import dataset

def __roblox_api_get(url: str, cookies = None, depth: int = 0) -> dict:
    resp = requests.get(url, cookies=cookies).json()

    if depth >= 20:
        return {}

    if "errors" in resp:
        time.sleep(random.uniform(0.8, 1.5)) # 0.8 - 1.5 secs sleep
        print(f"[ALERT!] Retrying.. {url}")
        print("[INFO!] ", resp)
        return __roblox_api_get(url, depth=depth+1)
    
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
    resp = __roblox_api_get(f"https://badges.roblox.com/v1/users/{user_id}/badges?limit=100&sortOrder=Desc&cursor={_cursor}")
    games: list[int] = [badge["awarder"]["id"] for badge in resp["data"]]

    if resp["nextPageCursor"]:
        games.extend(user_get_hist_games(user_id, _cursor=resp["nextPageCursor"]))

    return games

def game_convert_root_place_id(rpid: int) -> int:
    resp = __roblox_api_get(f"https://apis.roblox.com/universes/v1/places/{rpid}/universe")
    return resp["universeId"]

def game_get_details(game_ids: list[int]) -> list[dict]:
    N_GAMES_PER_CHUNK: int = 50 # roblox's api docs says 100 is the limit, but we can only do 50
    chunks = [game_ids[i:i + N_GAMES_PER_CHUNK] for i in range(0, len(game_ids), N_GAMES_PER_CHUNK)]

    games = []
    for chunk in chunks:
        resp = __roblox_api_get(f"https://games.roblox.com/v1/games?universeIds={",".join(map(str, chunk))}")
        games.extend([{
            "id":           game["id"],
            "rpid":         game["rootPlaceId"],
            "title":        emoji.replace_emoji(game["name"], r"").strip(),
            "description":  emoji.replace_emoji(re.sub(r"\r?\n", r"\\n", game["description"] or ""), r"").strip(),
            "genres":       [game["genre"], game["genre_l1"], game["genre_l2"]],
            "visits":       game["visits"],
            "favorite":     game["favoritedCount"],
        } for game in resp["data"]])

    return games

def scrap(uid: int):
    global users, games

    def scrap_user_information(uid: int):
        if uid in dataset.users:
            users[uid] = dataset.users[uid]
            return

        users[uid] = {}
        users[uid]["id"] = uid
        users[uid]["friends"] = user_get_friends(uid)
        try:
            # this endpoint doesn't work anymore wth..
            users[uid]["favorites"] = user_get_fav_games(uid)
        except:
            users[uid]["favorites"] = []
        users[uid]["history"] = []

        rpids: dict[int, int] = {game["rpid"]: game["id"] for game in dataset.games.values()}

        for rpid in user_get_hist_games(uid):
            if rpid in rpids:
                users[uid]["history"].append(rpids[rpid])
                continue

            game_id = game_convert_root_place_id(rpid)
            rpids[rpid] = game_id
            users[uid]["history"].append(game_id)

    scrap_user_information(uid)

    game_ids_to_be_scrapped = []
    for game_id in [id for id in users[uid]["favorites"] + list(set(users[uid]["history"]))]:
        if game_id in dataset.games:
            games[game_id] = dataset.games[game_id]
            continue
        
        game_ids_to_be_scrapped.append(game_id)

    for game in game_get_details(game_ids_to_be_scrapped):
        games[game["id"]] = game

if __name__ == "__main__":
    dataset.CSV_USERS_FILEPATH = "data/users--migrated.csv"
    dataset.CSV_GAMES_FILEPATH = "data/games--migrated.csv"

    dataset.__load()
    users: dict[int, dict] = dataset.users
    games: dict[int, dict] = dataset.games

    dataset.ensure_exist(dataset.CSV_USERS_FILEPATH)
    dataset.ensure_exist(dataset.CSV_GAMES_FILEPATH)

    uids = []

    N_USERS_PER_CHUNK: int = 5
    chunks = [uids[i:i + N_USERS_PER_CHUNK] for i in range(0, len(uids), N_USERS_PER_CHUNK)]
        
    for chunk in chunks:
        threads = [threading.Thread(target=scrap, args=(uid, )) for uid in chunk]
        for t in threads: t.start()
        for t in threads: t.join()

    dataset.dump(dataset.CSV_USERS_FILEPATH,
                 [{"id":        u["id"],
                   "favorites": "|".join(map(str, u["favorites"])), 
                   "history":   "|".join(map(str, u["history"])),
                   "friends":   "|".join(map(str, u["friends"]))} for u in users.values()],
                 ["id", "favorites", "history", "friends"])

    dataset.dump(dataset.CSV_GAMES_FILEPATH,
                 [{"id":           g["id"],
                   "rpid":         g["rpid"],
                   "title":        g["title"],
                   "description":  g["description"],
                   "genres":       "|".join(g["genres"]),
                   "visits":       g["visits"],
                   "favorite":     g["favorite"]} for g in games.values()],
                 ["id", "rpid", "title", "description", "genres", "visits", "favorite"])
