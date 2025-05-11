import csv
import io
import os
import pickle

CSV_GAMES_FILEPATH = "data/games.csv"
CSV_USERS_FILEPATH = "data/users.csv"

def load(path: str) -> list[dict[str, str]]:
    with open(path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

    return []

def load_nth_row(path: str, nth: int) -> set[int]:
    with open(path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)

        ids = [row[nth] for row in reader]
        if len(ids) >= 1:
            ids.pop(0)

        return set(map(int, ids))

    return set()

def dump(path: str, objects: list[dict], headers: list[str]):
    with open(path, mode="w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)

        if os.stat(path).st_size == 0:
            w.writeheader()
        
        w.writerows(objects)

def insert_headers(path: str, headers: list[str]) -> tuple[io.TextIOWrapper, csv.DictWriter]:
    f = open(path, mode="a", newline="", encoding="utf-8")
    w = csv.DictWriter(f, fieldnames=headers)

    if os.stat(path).st_size == 0:
        w.writeheader()

    return f, w

def ensure_exist(path: str) -> None:
    if not os.path.exists(path):
        open(path, "w").close()

__games: dict[int, dict] = {}
__users: dict[int, dict] = {}
__dataset: dict[str, dict] = {}

def __load():
    global __games, __users, __dataset

    ensure_exist(CSV_GAMES_FILEPATH)
    ensure_exist(CSV_USERS_FILEPATH)

    for game in load(CSV_GAMES_FILEPATH):
        game["id"] = int(game["id"])
        game["rpid"] = int(game["rpid"])
        game["visits"] = int(game["visits"])
        game["favorite"] = int(game["favorite"])
        game["genres"] = game["genres"].split("|")
        __games[game["id"]] = game

    for user in load(CSV_USERS_FILEPATH):
        user["id"] = int(user["id"])
        user["favorites"] = list(map(int, user["favorites"].split("|"))) if user["favorites"] != "" else []
        user["history"] = list(map(int, user["history"].split("|"))) if user["history"] != "" else []
        user["friends"] = list(map(int, user["friends"].split("|"))) if user["friends"] != "" else []
        __users[user["id"]] = user
    
    __dataset = {"games": __games, "users": __users}

def __load_embeddings() -> dict:
    from os.path import exists

    if not exists("data/embeddings.pkl"):
        with open("data/embeddings.pkl", "wb") as f:
            pickle.dump({}, f)

    with open("data/embeddings.pkl", "rb") as f:
        embeddings = pickle.load(f)
        return embeddings
    
    return {}

def __save_embeddings():
    with open("data/embeddings.pkl", "wb") as f:
        embeddings = {k: v["__embed"] for k, v in __games.items()}
        pickle.dump(embeddings, f)

def __process_games():
    import model
    import time
    from collections import Counter

    batch = -1

    for id, game in __games.items():
        if batch == 0:
            break

        if game["title"] == "[ Content Deleted ]" or game["genres"][1] != "":
            continue

        start = time.time()

        genres = Counter([__games[pred]["genres"][1] for pred in model.similar([id], k=50)]).most_common()
        game["genres"][1] = next(filter(lambda genre: genre[0] != "", genres), ("", ))[0]

        end = time.time()
        print(f"{id} Elapsed time: {end - start:.4f} seconds")

        batch -= 1

    dump(CSV_GAMES_FILEPATH, [{
            "id":            game["id"],
            "rpid":          game["rpid"],
            "title":         game["title"],
            "description":   game["description"],
            "genres":        "|".join(game["genres"]),
            "visits":        game["visits"],
            "favorite":      game["favorite"],
            "created":       game["created"],
            "updated":       game["updated"],
        } for game in __games.values()], 
        ["id", "rpid", "title", "description", "genres", "visits", "favorite", "created", "updated"])

def __get(id: int, d: dict) -> dict:
    if id not in d:
        return None

    return d[id]

def game_get(id: int) -> dict:
    return __get(id, __games)

def user_get(id: int) -> dict:
    return __get(id, __users)

def __random(d: dict) -> dict:
    import random

    ids = list(d.keys())
    id = ids[random.randint(0, len(ids) - 1)]
    return d[id]

def game_get_random() -> dict:
    return __random(__games)

def user_get_random() -> dict:
    return __random(__users)

