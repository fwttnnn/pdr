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

        if not recsys.dataset.game_get(id):
            return starlette.responses.JSONResponse({ "error": "Specified game does not exist" })

        games = [recsys.dataset.game_get(rec[1]) for rec in recsys.model.similar([id], k=n)]
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

    def sample(lst: list, n: int) -> list:
        start = random.randint(0, max(0, (len(lst) - n) - 1))
        return lst[start:start+n]

    hist = sample(user["favorites"] + user["history"], n=50+k)
    future = hist[k:] # this is the list of what the predictions should be tested on
    hist = hist[:k]

    hit = 0
    idcg = 1
    dcg = 0.0

    for idx, p in enumerate(recsys.model.similar(hist, k)):
        game = recsys.dataset.game_get(p[1])
        hit += int(game["id"] in future)

        if game["id"] in future:
            dcg = max(dcg, 1 / math.log2(idx + 2))

        print(f"{p[1]} \t ::= {game["id"] in future} @@@ https://roblox.com/games/{game["rpid"]}")
    
    print(f"Hit@{k}: {hit}, NDCG@{k}: {dcg / idcg}")

if __name__ == "__main__":
    import recsys.dataset
    import recsys.model
    import sys

    if "--serve" in sys.argv:
        __run_server()
        sys.exit(0)
    
    if "--test" in sys.argv:
        for user in recsys.dataset.__users.values():
            __test(user, k=10)
            print()
        sys.exit(0)

    game = recsys.dataset.game_get_random()
    print(f"games similar to '{game["title"]}' (https://roblox.com/games/{game["rpid"]}):")
    for __game in recsys.model.similar([game["id"]], k=10):
        score, id = __game
        __game = recsys.dataset.game_get(id)

        print(f"{score} '{__game["title"]}' (https://roblox.com/games/{__game["rpid"]})")
