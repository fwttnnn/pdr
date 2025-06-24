#!/usr/bin/env python

"""
Recommender system for Roblox.
"""

def __run_server():
    import starlette.applications
    import starlette.responses
    import starlette.routing
    import starlette.requests
    import requests
    import uvicorn

    async def __html_home(request: starlette.requests.Request):
        with open("lib/ui/home.html", "r", encoding="utf-8") as f:
            return starlette.responses.HTMLResponse(f.read())

    async def __html_recommend(request: starlette.requests.Request):
        with open("lib/ui/recommend.html", "r", encoding="utf-8") as f:
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

def test(user: dict, k=10) -> tuple[int, float, float]:
    hist__ = list(dict.fromkeys(user["favorites"] + list(dict.fromkeys(user["history"]).keys())).keys())
    hist__ = [dataset.games[id] for id in hist__ if id in dataset.games]

    def group():
        from collections import Counter

        most_liked_genres = set()
        n_games = 0
        
        for (genre, count) in Counter([game["genres"][1] for game in hist__]).most_common():
            most_liked_genres.add(genre)
            n_games += count

            if n_games >= 3:
                break
        
        return most_liked_genres

    def metrics(hist: list, predictions: list) -> tuple[int, float, float]:
        import math

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

    genres = group()
    hist = [game["id"] for game in hist__ if game["genres"][1] in genres][:3]
    future = [game["id"] for game in hist__]

    for id in hist:
        game = dataset.games[id]
        print(f"{game['id']} \t ::= https://roblox.com/games/{game['rpid']}")

    predictions = model.similar(hist, k)
    for pred in predictions:
        game = dataset.games[pred]
        print(f"{pred} \t ::= {game['id'] in future} @@@ https://roblox.com/games/{game['rpid']}")
    
    hit, ndcg, precision = metrics(future, predictions)
    print(f"Hit@{k}: {hit}, NDCG@{k}: {ndcg:.4f}, Precision@{k}: {precision:.4f}")
    print(genres)
    
    return hit, ndcg, precision

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

    if False:
        dataset.__process_games()
        sys.exit(0)

    if args.serve:
        __run_server()
        sys.exit(0)
    
    if args.test:
        k         = 10
        hit       = 0
        ndcg      = 0
        precision = 0
        averages: dict[int, tuple | None] = {50:   None,
                                             100:  None,
                                             300:  None,
                                             500:  None,
                                             1000: None}
        
        users = [user for user in dataset.users.values() if len(user["favorites"]) + len(user["history"]) >= k + 3]
        for i, user in enumerate(users):
            print(f"{i + 1} testing user: {user['id']}")
            metrics = test(user, k)

            hit       += (1 if metrics[0] else 0)
            ndcg      += metrics[1]
            precision += metrics[2]

            print()

            n = i + 1
            if n in averages:
                averages[n] = (hit / n, ndcg / n, precision / n)

        for n, avg in averages.items():
            if avg is None:
                break

            print(f"{n}: Average HR@{k}: {avg[0]:.2f}, Average NDCG@{k}: {avg[1]:.2f}, Average Precision@{k}: {avg[2]:.2f}")
            print(f"{n}: Average HR@{k}: {avg[0]:.4f}, Average NDCG@{k}: {avg[1]:.4f}, Average Precision@{k}: {avg[2]:.4f}")

        users_len  = len(users)
        hit       /= users_len
        ndcg      /= users_len
        precision /= users_len
        print(f"{users_len} (All): Average HR@{k}: {hit:.2f}, Average NDCG@{k}: {ndcg:.2f}, Average Precision@{k}: {precision:.2f}")
        print(f"{users_len} (All): Average HR@{k}: {hit:.4f}, Average NDCG@{k}: {ndcg:.4f}, Average Precision@{k}: {precision:.4f}")
        sys.exit(0)

    game = dataset.random(dataset.games)
    print(f"games similar to '{game['title']}' (https://roblox.com/games/{game['rpid']}):")
    for pred in model.similar([game["id"]], k=10):
        __game = dataset.games[pred]
        print(f"'{__game['title']}' (https://roblox.com/games/{__game['rpid']})")
