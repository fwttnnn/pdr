#!/usr/bin/env python

"""
Recommender system for Roblox.
"""

def serve():
    import starlette.applications
    import starlette.responses
    import starlette.routing
    import starlette.requests
    import requests
    import uvicorn

    async def __html_home(request: starlette.requests.Request):
        with open("ui/home.html", "r", encoding="utf-8") as f:
            return starlette.responses.HTMLResponse(f.read())

    async def __html_recommend(request: starlette.requests.Request):
        with open("ui/recommend.html", "r", encoding="utf-8") as f:
            return starlette.responses.HTMLResponse(f.read())

    async def __proxy_icons(request: starlette.requests.Request):
        data = requests.get(f"https://thumbnails.roblox.com/v1/games/icons?universeIds={request.query_params['ids']}&returnPolicy=PlaceHolder&size=128x128&format=Webp&isCircular=false").json()
        return starlette.responses.JSONResponse(data)
    
    async def __api_games(request: starlette.requests.Request):
        page = request.query_params["page"] if "page" in request.query_params else 0
        try:
            page = int(page)
        except:
            return starlette.responses.JSONResponse({ "error": "Specified page should be an integer" })

        def batch(lst: list, n: int) -> list[list]:
            return [lst[i:i + n] for i in range(0, len(lst), n)]

        chunks = batch(list(dataset.games.values()), 50)
        return starlette.responses.JSONResponse({
            "data": {
                "games": chunks[page],
                "next": page + 1 if (page + 1) < len(chunks) else None,
            }
        })

    async def __api_random(request: starlette.requests.Request):
        n = request.query_params["n"] if "n" in request.query_params else 10
        try:
            n = int(n)
        except:
            return starlette.responses.JSONResponse({ "error": "Specified n should be an integer" })

        game = dataset.__random(dataset.games)
        return starlette.responses.JSONResponse({
            "data": {
                "game": game,
                "recommendations": [dataset.games[pred] for pred in model.similar([game["id"]], k=n)],
            }
        })

    async def __api_recommend(request: starlette.requests.Request):
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

        if not dataset.games[id]:
            return starlette.responses.JSONResponse({ "error": "Specified game does not exist" })

        return starlette.responses.JSONResponse({
            "data": [dataset.games[pred] for pred in model.similar([id], k=n)]
        })

    uvicorn.run(starlette.applications.Starlette(debug=False, routes=[
        starlette.routing.Route("/", __html_home),
        starlette.routing.Route("/recommend/{id}", __html_recommend),
        starlette.routing.Route("/proxy/icons", __proxy_icons),
        starlette.routing.Route("/api/v1/games", __api_games),
        starlette.routing.Route("/api/v1/random", __api_random),
        starlette.routing.Route("/api/v1/recommend", __api_recommend)
    ]))

def test(k: int = 10):
    import dataset

    def group_most_liked_genres(games: list[dict]) -> set[str]:
        from collections import Counter

        most_liked_genres = set()
        games_total = 0
        
        for (genre, total) in Counter([game["genres"][1] for game in games]).most_common():
            most_liked_genres.add(genre)
            games_total += total

            if games_total >= PREVIOUSLY_PLAYED_GAMES_LIMIT:
                break
        
        return most_liked_genres

    def metrics(history: list, predictions: list) -> tuple[int, float, float]:
        import math

        relevances = [int(p in history) for p in predictions]
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

    hit       = 0
    ndcg      = 0
    precision = 0
    averages: dict[int, tuple | None] = {50:   None,
                                         100:  None,
                                         300:  None,
                                         500:  None,
                                         1000: None}
    
    users = [user for user in dataset.users.values()]
    PREVIOUSLY_PLAYED_GAMES_LIMIT = 3

    for i, user in enumerate(users):
        history: list[int] = list(dict.fromkeys(user["favorites"] + list(dict.fromkeys(user["history"]).keys())).keys())
        games: list[dict] = [dataset.games[id] for id in history if id in dataset.games]
        genres: set[str] = group_most_liked_genres(games)

        played: list[int] = [game["id"] for game in games if game["genres"][1] in genres][:PREVIOUSLY_PLAYED_GAMES_LIMIT]
        future: list[int] = [game["id"] for game in games if game not in played]

        predictions = model.similar(played, k)
        __hit, __ndcg, __precision = metrics(future, predictions)

        hit       += (1 if __hit else 0)
        ndcg      += __ndcg
        precision += __precision

        n = i + 1
        if n in averages:
            averages[n] = (hit / n, ndcg / n, precision / n)

    users_len  = len(users)
    hit       /= users_len
    ndcg      /= users_len
    precision /= users_len
    averages[users_len] = (hit, ndcg, precision)

    for n, avg in sorted(averages.items()):
        if avg is None:
            break

        print(f"{n}: Average HR@{k}: {avg[0]:.2f}, Average NDCG@{k}: {avg[1]:.2f}, Average Precision@{k}: {avg[2]:.2f}")
        print(f"{n}: Average HR@{k}: {avg[0]:.4f}, Average NDCG@{k}: {avg[1]:.4f}, Average Precision@{k}: {avg[2]:.4f}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
                    prog="Risperidone",
                    description="Recommender system for Roblox.")
    parser.add_argument("-s", "--serve", action="store_true", help="spin up a web server")
    parser.add_argument("-t", "--test", action="store_true", help="calculate Risperidone's accuracy")
    parser.add_argument("-v", "--verbose", action="store_true", help="turn on debugging")
    args = parser.parse_args()

    if args.verbose:
        import logging
        logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG)

    import dataset
    import model
    import embeddings
    import sys

    dataset.load()
    embeddings.precompute()

    if args.serve:
        serve()
        sys.exit(0)
    
    if args.test:
        test(k=10)
        sys.exit(0)

    game = dataset.random(dataset.games)
    print(f"games similar to '{game['title']}' (https://roblox.com/games/{game['rpid']}):")
    for pred in model.similar([game["id"]], k=10):
        __game = dataset.games[pred]
        print(f"'{__game['title']}' (https://roblox.com/games/{__game['rpid']})")
