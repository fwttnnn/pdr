import logging
import csv
import os

# 512 MB
csv.field_size_limit((1024 * 1024) * 512)

CSV_GAMES_FILEPATH = "data/games.csv"
CSV_USERS_FILEPATH = "data/users.csv"

embeddings: dict       = {}
games: dict[int, dict] = {}
users: dict[int, dict] = {}

def load_csv(path: str) -> list[dict[str, str]]:
    if not os.path.exists(path):
        open(path, "w").close()

    with open(path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

def dump_csv(path: str, objects: list[dict], headers: list[str]):
    with open(path, mode="w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)

        if os.stat(path).st_size == 0:
            w.writeheader()
        
        w.writerows(objects)

def load():
    logger = logging.getLogger(__name__)

    logger.info(f"Risperidone: loading games csv from {CSV_GAMES_FILEPATH}")
    for game in load_csv(CSV_GAMES_FILEPATH):
        game["id"] = int(game["id"])
        game["rpid"] = int(game["rpid"])
        game["visits"] = int(game["visits"])
        game["favorite"] = int(game["favorite"])
        game["genres"] = game["genres"].split("|")
        games[game["id"]] = game
    logger.info(f"Risperidone: loaded games successfully")

    logger.info(f"Risperidone: loading users csv from {CSV_USERS_FILEPATH}")
    for user in load_csv(CSV_USERS_FILEPATH):
        user["id"] = int(user["id"])
        user["favorites"] = list(map(int, user["favorites"].split("|"))) if user["favorites"] != "" else []
        user["history"] = list(map(int, user["history"].split("|"))) if user["history"] != "" else []
        user["friends"] = list(map(int, user["friends"].split("|"))) if user["friends"] != "" else []
        users[user["id"]] = user
    logger.info(f"Risperidone: loaded users successfully")

def random(d: dict = games) -> dict:
    import random

    id = random.choice(list(d.keys()))
    return d[id]
