import recsys.csv

__dataset: dict[int, dict[str, str]] = {int(game["id"]): game for game in recsys.csv.load(recsys.csv.CSV_GAMES_FILEPATH)}

def get(id: int) -> dict[str, str]:
    return __dataset[id]

def random() -> dict[str, str]:
    import random

    ids = list(__dataset.keys())
    id = ids[random.randint(0, len(ids))]
    return __dataset[id]
