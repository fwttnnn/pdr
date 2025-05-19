#!/usr/bin/env python

"""
Roblox game scraper based on user's fav list and badges.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).absolute().parent.parent.joinpath("lib")))

import time
import random
import concurrent.futures
import re
import requests
import emoji
import dataset

def __roblox_api_get(url: str, cookies = None, retrying = False) -> dict:
    print(url + (" retrying.." if retrying else ""), file=sys.stderr)

    try:
        resp = requests.get(url, cookies=cookies).json()
    except:
        time.sleep(random.uniform(0.8, 1.5)) # 0.8 - 1.5 secs sleep
        return __roblox_api_get(url, retrying=True)

    if "errors" in resp:
        time.sleep(random.uniform(0.8, 1.5)) # 0.8 - 1.5 secs sleep
        return __roblox_api_get(url, retrying=True)
    
    return resp

def __roblox_api_post(url: str, cookies = None, data = {}, retrying = False) -> dict:
    print(url + (" retrying.." if retrying else ""), file=sys.stderr)

    try:
        resp = requests.post(url, cookies=cookies, json=data).json()
    except:
        time.sleep(random.uniform(0.8, 1.5)) # 0.8 - 1.5 secs sleep
        return __roblox_api_post(url, retrying=True)

    if "errors" in resp:
        time.sleep(random.uniform(0.8, 1.5)) # 0.8 - 1.5 secs sleep
        return __roblox_api_post(url, retrying=True)
    
    return resp

def user_get_ids_by_usernames(usernames: list[str]) -> list[int]:
    ids =  []

    for chunk in batch(usernames, 50):
        resp = __roblox_api_post("https://users.roblox.com/v1/usernames/users", data={
            "usernames": chunk,
            "excludeBannedUsers": True })
        ids.extend([u["id"] for u in resp["data"]])
    
    return ids

def user_get_friends(user_id: int) -> list[int]:
    resp = __roblox_api_get(f"https://friends.roblox.com/v1/users/{user_id}/friends")
    return [user_detail["id"] for user_detail in resp["data"]]

def user_get_fav_games(user_id: int, _cursor: str = "") -> list[int]:
    resp = __roblox_api_get(f"https://games.roblox.com/v2/users/{user_id}/favorite/games?limit=100&cursor={_cursor}")
    games: list[int] = [game["id"] for game in resp["data"]]

    if resp["nextPageCursor"]:
        games.extend(user_get_fav_games(user_id, _cursor=resp["nextPageCursor"]))

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
    games = []

    for chunk in batch(game_ids, 50):
        resp = __roblox_api_get(f"https://games.roblox.com/v1/games?universeIds={','.join(map(str, chunk))}")
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
    dataset.users[uid] = {}
    dataset.users[uid]["id"] = uid
    dataset.users[uid]["friends"] = user_get_friends(uid)
    dataset.users[uid]["favorites"] = user_get_fav_games(uid)
    dataset.users[uid]["history"] = []

    rpids: dict[int, int] = {game["rpid"]: game["id"] for game in dataset.games.values()}
    for rpid in user_get_hist_games(uid):
        if rpid in rpids:
            dataset.users[uid]["history"].append(rpids[rpid])
            continue

        game_id = game_convert_root_place_id(rpid)
        rpids[rpid] = game_id
        dataset.users[uid]["history"].append(game_id)

    for game in game_get_details([id for id in list(set(dataset.users[uid]["favorites"] + list(set(dataset.users[uid]["history"])))) if id not in dataset.games]):
        dataset.games[game["id"]] = game

def batch(lst: list, n: int) -> list[list]:
    return [lst[i:i + n] for i in range(0, len(lst), n)]

if __name__ == "__main__":
    dataset.__load()

    if "--update" in sys.argv:
        games = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            chunks = batch(list(dataset.games.keys()), 50)
            futures = [executor.submit(game_get_details, chunk) for chunk in chunks]

            for future in concurrent.futures.as_completed(futures):
                for game in future.result():
                    games[game["id"]] = game
                
        dataset.dump("data/games--updated.csv",
                     [{"id":           g["id"],
                       "rpid":         g["rpid"],
                       "title":        g["title"],
                       "description":  g["description"],
                       "genres":       "|".join(g["genres"]),
                       "visits":       g["visits"],
                       "favorite":     g["favorite"]} for g in games.values()],
                     ["id", "rpid", "title", "description", "genres", "visits", "favorite"])
        
        sys.exit(0)
    
    if "--from-usernames" in sys.argv:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            f = open(sys.argv[-1], "r")
            usernames = [line.strip() for line in f]
            f.close()

            chunks = batch(usernames, 100)
            futures = [executor.submit(user_get_ids_by_usernames, chunk) for chunk in chunks]

            # TODO: need further investigation
            #       doesn't fully scrap all of the users
            for future in concurrent.futures.as_completed(futures):
                for id in future.result():
                    print(id)

        sys.exit(0)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        uids = []

        for chunk in batch(uids, 10):
            futures = [executor.submit(scrap, uid) for uid in chunk]
            for _ in concurrent.futures.as_completed(futures): pass

            dataset.dump(dataset.CSV_USERS_FILEPATH,
                        [{"id":        u["id"],
                          "favorites": "|".join(map(str, u["favorites"])), 
                          "history":   "|".join(map(str, u["history"])),
                          "friends":   "|".join(map(str, u["friends"]))} for u in dataset.users.values()],
                          ["id", "favorites", "history", "friends"])

            dataset.dump(dataset.CSV_GAMES_FILEPATH,
                        [{"id":           g["id"],
                          "rpid":         g["rpid"],
                          "title":        g["title"],
                          "description":  g["description"],
                          "genres":       "|".join(g["genres"]),
                          "visits":       g["visits"],
                          "favorite":     g["favorite"]} for g in dataset.games.values()],
                          ["id", "rpid", "title", "description", "genres", "visits", "favorite"])
