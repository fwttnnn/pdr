import recsys.csv

__dataset: dict[int, dict[str, str]] = {int(game["id"]): game for game in recsys.csv.load(recsys.csv.CSV_GAMES_FILEPATH)}

def get(id: int) -> dict[str, str]:
    return __dataset[id]

def to_list() -> list[dict[str, str]]:
    return __dataset.values()

def to_list_without(game_ids: list[int]) -> list[dict[str, str]]:
    excludes = set(game_ids)
    lst = []

    for game in __dataset.values():
        if int(game["id"]) in excludes:
            continue

        lst.append(game)
    
    return lst
