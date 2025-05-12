import csv
import io
import os
import pickle

EMBEDDINGS_FILEPATH = "data/embeddings.pkl"
CSV_GAMES_FILEPATH  = "data/games.csv"
CSV_USERS_FILEPATH  = "data/users.csv"

embeddings: dict       = {}
games: dict[int, dict] = {}
users: dict[int, dict] = {}

def load(path: str) -> list[dict[str, str]]:
    with open(path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

    return []

def dump(path: str, objects: list[dict], headers: list[str]):
    with open(path, mode="w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)

        if os.stat(path).st_size == 0:
            w.writeheader()
        
        w.writerows(objects)

def ensure_exist(path: str):
    if not os.path.exists(path):
        open(path, "w").close()

def __load():
    global games, users

    ensure_exist(CSV_GAMES_FILEPATH)
    ensure_exist(CSV_USERS_FILEPATH)

    for game in load(CSV_GAMES_FILEPATH):
        game["id"] = int(game["id"])
        game["rpid"] = int(game["rpid"])
        game["visits"] = int(game["visits"])
        game["favorite"] = int(game["favorite"])
        game["genres"] = game["genres"].split("|")
        games[game["id"]] = game

    for user in load(CSV_USERS_FILEPATH):
        user["id"] = int(user["id"])
        user["favorites"] = list(map(int, user["favorites"].split("|"))) if user["favorites"] != "" else []
        user["history"] = list(map(int, user["history"].split("|"))) if user["history"] != "" else []
        user["friends"] = list(map(int, user["friends"].split("|"))) if user["friends"] != "" else []
        users[user["id"]] = user

def __load_embeddings() -> dict:
    global embeddings

    if not os.path.exists(EMBEDDINGS_FILEPATH):
        with open(EMBEDDINGS_FILEPATH, "wb") as f:
            pickle.dump({}, f)

    with open(EMBEDDINGS_FILEPATH, "rb") as f:
        embeddings = pickle.load(f)
        return embeddings
    
def __save_embeddings():
    global embeddings

    with open(EMBEDDINGS_FILEPATH, "wb") as f:
        pickle.dump(embeddings, f)

def __process_games():
    import model
    import time
    from collections import Counter

    batch = -1

    for id, game in games.items():
        if batch == 0:
            break

        if game["title"] == "[ Content Deleted ]" or game["genres"][1] != "":
            continue

        start = time.time()

        genres = Counter([games[pred]["genres"][1] for pred in model.similar([id], k=50)]).most_common()
        game["genres"][1] = next(filter(lambda genre: genre[0] != "", genres), ("", ))[0]

        end = time.time()
        print(f"{id} Elapsed time: {end - start:.4f} seconds")

        batch -= 1

    dump(CSV_GAMES_FILEPATH,
         [{"id":           g["id"],
           "rpid":         g["rpid"],
           "title":        g["title"],
           "description":  g["description"],
           "genres":       "|".join(g["genres"]),
           "visits":       g["visits"],
           "favorite":     g["favorite"]} for g in games.values()],
         ["id", "rpid", "title", "description", "genres", "visits", "favorite"])

def __random(d: dict) -> dict:
    import random

    ids = list(d.keys())
    id = ids[random.randint(0, len(ids) - 1)]
    return d[id]
