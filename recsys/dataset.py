import recsys.csv

__games: dict[int, dict[str, str]] = {int(game["id"]): game for game in recsys.csv.load(recsys.csv.CSV_GAMES_FILEPATH)}
__users: dict[int, dict[str, str]] = {int(user["id"]): user for user in recsys.csv.load(recsys.csv.CSV_USERS_FILEPATH)}
__dataset: dict[str, dict] = {"games": __games, "users": __users}

def __get(id: int, d: dict) -> dict[str, str]:
    return d[id]

def game_get(id: int) -> dict[str, str]:
    return __get(id, __games)

def user_get(id: int) -> dict[str, str]:
    return __get(id, __users)

def __random(d: dict) -> dict[str, str]:
    import random

    ids = list(d.keys())
    id = ids[random.randint(0, len(ids))]
    return d[id]

def game_get_random() -> dict[str, str]:
    return __random(__games)

def user_get_random() -> dict[str, str]:
    return __random(__users)

