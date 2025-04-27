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

        games = [recsys.dataset.game_get(rec[1]) for rec in recsys.model.similar(id, k=n)]
        games = list(map(lambda game: {k: v for k, v in game.items() if k not in {"__embed"}}, games))

        return starlette.responses.JSONResponse({
            "data": games
        })

    uvicorn.run(starlette.applications.Starlette(debug=False, routes=[
        starlette.routing.Route("/recommend", recommend)
    ]))

if __name__ == "__main__":
    import recsys.dataset
    import recsys.model
    import sys

    if "--serve" in sys.argv:
        __run_server()
        sys.exit(0)

    game = recsys.dataset.game_get_random()
    print(f"games similar to '{game["title"]}' (https://roblox.com/games/{game["rpid"]}):")
    for __game in recsys.model.similar(int(game["id"]), k=10):
        score, id = __game
        __game = recsys.dataset.game_get(id)

        print(f"{score} '{__game["title"]}' (https://roblox.com/games/{__game["rpid"]})")
