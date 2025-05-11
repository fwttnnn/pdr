#!/usr/bin/env python

"""
Recommender system for Roblox.
"""

def __run_server():
    import starlette.applications
    import starlette.responses
    import starlette.routing
    import starlette.requests
    import uvicorn

    async def recommend(request: starlette.requests.Request):
        if "id" not in request.query_params:
            return starlette.responses.JSONResponse({ "error": "No id specified" })

        id = request.query_params["id"]
        try:
            id = int(id)
        except:
            return starlette.responses.JSONResponse({ "error": "Specified id should be an integer" })

        n = request.query_params["n"] if "n" in request.query_params else 10
        try:
            n = int(n)
        except:
            return starlette.responses.JSONResponse({ "error": "Specified n should be an integer" })

        if not dataset.game_get(id):
            return starlette.responses.JSONResponse({ "error": "Specified game does not exist" })

        games = [dataset.game_get(pred) for pred in model.similar([id], k=n)]
        games = list(map(lambda game: {k: v for k, v in game.items() if k not in {"__embed"}}, games))

        return starlette.responses.JSONResponse({
            "data": games
        })

    uvicorn.run(starlette.applications.Starlette(debug=False, routes=[
        starlette.routing.Route("/recommend", recommend)
    ]))

def __test(user: dict, k=10):
    import math

    hist__ = list(dict.fromkeys(user["favorites"] + list(dict.fromkeys(user["history"]).keys())).keys())
    hist__ = [dataset.__games[id] for id in hist__ if id in dataset.__games]

    def group(games: list[dict]) -> dict[str, list]:
        groups: dict[str, list] = {}

        for game in games:
            genre = game["genres"][1]

            if genre not in groups:
                groups[genre] = []

            groups[genre].append(game["id"])

        return groups

    def metrics(hist: list, predictions: list):
        relevances = [int(p in hist) for p in predictions]
        ideal_relevances = sorted(relevances, reverse=True)
        k = len(relevances)

        hit = 0
        dcg = 0.0
        idcg = 0.0

        for i in range(k):
            logd = math.log2(i + 2)
            dcg += relevances[i] / logd
            idcg += ideal_relevances[i] / logd

            hit += relevances[i]

        ndcg = (dcg / idcg if idcg > 0 else 0.0)
        precision = hit / k
        return hit, ndcg, precision
    
    from collections import Counter
    most_liked_genres = set()
    ngames = 0
    
    for (genre, count) in Counter([game["genres"][1] for game in hist__]).most_common():
        most_liked_genres.add(genre)
        ngames += count

        if ngames >= 3:
            break

    hist = [game["id"] for game in hist__ if game["genres"][1] in most_liked_genres][:3]
    future = [game["id"] for game in hist__]

    for id in hist:
        game = dataset.game_get(id)
        print(f"{game["id"]} \t ::= https://roblox.com/games/{game["rpid"]}")

    predictions = model.similar(hist, k)
    for pred in predictions:
        game = dataset.game_get(pred)
        print(f"{pred} \t ::= {game["id"] in future} @@@ https://roblox.com/games/{game["rpid"]}")
    
    hit, ndcg, precision = metrics(future, predictions)
    print(f"Hit@{k}: {hit}, NDCG@{k}: {ndcg}, Precision@{k}: {precision}")
    print(most_liked_genres)
    
    return hit, ndcg, precision

if __name__ == "__main__":
    import dataset
    import model
    import sys

    if "--process" in sys.argv:
        dataset.__process_games()
        sys.exit(0)

    if "--serve" in sys.argv:
        __run_server()
        sys.exit(0)
    
    if "--test" in sys.argv:
        k             = 10
        avg_hit       = 0
        avg_ndcg      = 0
        avg_precision = 0

        for user in dataset.__users.values():
            print(f"testing user: {user["id"]}")
            hit, ndcg, precision = __test(user, k)
            avg_hit += hit
            avg_ndcg += ndcg
            avg_precision += precision
            print()

        users_len = len(dataset.__users)
        avg_hit       /= users_len
        avg_ndcg      /= users_len
        avg_precision /= users_len
        print(f"Average Hit@{k}: {avg_hit}, Average NDCG@{k}: {avg_ndcg}, Average Precision@{k}: {avg_precision}")
        sys.exit(0)

    game = dataset.game_get_random()
    print(f"games similar to '{game["title"]}' (https://roblox.com/games/{game["rpid"]}):")
    for pred in model.similar([game["id"]], k=10):
        __game = dataset.game_get(pred)
        print(f"'{__game["title"]}' (https://roblox.com/games/{__game["rpid"]})")
