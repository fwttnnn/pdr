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

        games = [dataset.game_get(rec[1]) for rec in model.similar([id], k=n)]
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

    nmetrics      = 0
    avg_hit       = 0
    avg_ndcg      = 0
    avg_precision = 0

    for genre, hist in group(hist__).items():
        hist = hist[:3]
        future = [game["id"] for game in hist__]
        
        for id in hist:
            game = dataset.game_get(id)
            print(f"{game["id"]} \t ::= https://roblox.com/games/{game["rpid"]}")

        predictions = model.similar(hist, k)
        for p in predictions:
            game = dataset.game_get(p[1])
            print(f"{p[1]} \t ::= {game["id"] in future} @@@ https://roblox.com/games/{game["rpid"]}")
        
        hit, ndcg, precision = metrics(future, [p[1] for p in predictions])
        print(f"Hit@{k}: {hit}, NDCG@{k}: {ndcg}, Precision@{k}: {precision}")
        print(genre)
        print()

        nmetrics += 1
        avg_hit += hit
        avg_ndcg += ndcg
        avg_precision += precision

    avg_hit /= nmetrics
    avg_ndcg /= nmetrics
    avg_precision /= nmetrics
    print(f"Average Hit@{k}: {avg_hit}, Average NDCG@{k}: {avg_ndcg}, Average Precision@{k}: {avg_precision}")

    return avg_hit, avg_ndcg, avg_precision

if __name__ == "__main__":
    import dataset
    import model
    import sys

    if "--serve" in sys.argv:
        __run_server()
        sys.exit(0)
    
    if "--test" in sys.argv:
        for user in dataset.__users.values():
            print(f"testing user: {user["id"]}")
            __test(user, k=10)
            print()

        sys.exit(0)

    game = dataset.game_get_random()
    print(f"games similar to '{game["title"]}' (https://roblox.com/games/{game["rpid"]}):")
    for __game in model.similar([game["id"]], k=10):
        score, id = __game
        __game = dataset.game_get(id)

        print(f"{score} '{__game["title"]}' (https://roblox.com/games/{__game["rpid"]})")
