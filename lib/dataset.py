import csv
import os

# 512 MB
csv.field_size_limit((1024 * 1024) * 512)

CSV_GAMES_FILEPATH = "data/games.csv"
CSV_USERS_FILEPATH = "data/users.csv"

embeddings: dict       = {}
games: dict[int, dict] = {}
users: dict[int, dict] = {}

def load(path: str) -> list[dict[str, str]]:
    if not os.path.exists(path):
        open(path, "w").close()

    with open(path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

def dump(path: str, objects: list[dict], headers: list[str]):
    with open(path, mode="w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)

        if os.stat(path).st_size == 0:
            w.writeheader()
        
        w.writerows(objects)

def __load():
    global games, users

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

def __process_games():
    import model
    import time
    from collections import Counter

    global games, users
    
    ids = [id for id in games.keys() if games[id]["genres"][1] == ""]
    ids_length = len(ids)

    for i, id in enumerate(ids):
        start = time.time()

        genres = Counter([games[pred]["genres"][1] for pred in model.similar([id], k=50)]).most_common()
        games[id]["genres"][1] = next(filter(lambda genre: genre[0] != "", genres), ("", ))[0]

        end = time.time()
        print(f"{id} Elapsed time: {end - start:.4f} seconds ({i + 1} out of {ids_length})")

        if i % 200 == 0:
            print("Saving..")
            dump(CSV_GAMES_FILEPATH,
                [{"id":           g["id"],
                  "rpid":         g["rpid"],
                  "title":        g["title"],
                  "description":  g["description"],
                  "genres":       "|".join(g["genres"]),
                  "visits":       g["visits"],
                  "favorite":     g["favorite"]} for g in games.values()],
                  ["id", "rpid", "title", "description", "genres", "visits", "favorite"])

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

    id = random.choice(list(d.keys()))
    return d[id]
