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
    import random

    hist = list(dict.fromkeys(user["favorites"] + list(dict.fromkeys(user["history"]).keys())).keys())
    hist = [dataset.__games[id] for id in hist]
    
    group: dict[str, list] = {}
    for g in hist:
        x = g["genres"].lower().split("|")[1]
        if x not in group:
            group[x] = []

        group[x].append((g["id"], g["title"]))

    genre = random.choice(list(group.keys()))
    games = group[genre]

    hist = [g[0] for g in games]
    CHANGE_THIS_LATER = 3
    future = hist[CHANGE_THIS_LATER:]
    hist = hist[:CHANGE_THIS_LATER]

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

    predictions = model.similar(hist, k)
    for p in predictions:
        game = dataset.game_get(p[1])
        print(f"{p[1]} \t ::= {game["id"] in future} @@@ https://roblox.com/games/{game["rpid"]}")
    
    return metrics(future, [p[1] for p in predictions])

if __name__ == "__main__":
    import dataset
    import model
    import sys

    if "--serve" in sys.argv:
        __run_server()
        sys.exit(0)
    
    if "--test" in sys.argv:
        k = 10
        total = 0.0

        for user in dataset.__users.values():
            hit, ndcg, precision = __test(user, k=k)
            print(f"Hit@{k}: {hit}, NDCG@{k}: {ndcg}, Precision@{k}: {precision}")
            print()
            total += precision

        avg = total / len(dataset.__users.values())
        print(f"precision avg: {avg}")
        sys.exit(0)

    game = dataset.game_get_random()
    print(f"games similar to '{game["title"]}' (https://roblox.com/games/{game["rpid"]}):")
    for __game in model.similar([game["id"]], k=10):
        score, id = __game
        __game = dataset.game_get(id)

        print(f"{score} '{__game["title"]}' (https://roblox.com/games/{__game["rpid"]})")
