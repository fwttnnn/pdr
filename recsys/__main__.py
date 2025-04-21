#!/usr/bin/env python

"""
Recommender system for Roblox.
"""

if __name__ == "__main__":
    import recsys
    import re
    from . import csv

    CSV_GAMES_FILEPATH = "data/games.csv"
    CSV_USERS_FILEPATH = "data/users.csv"

    csv.ensure_exist(CSV_GAMES_FILEPATH)
    games = csv.load(CSV_GAMES_FILEPATH)

    def __lemmatize(game: dict[str, str]) -> str:
        desc = re.sub(r"\\n", r"\n", game["description"].lower())
        doc = recsys.lemmatize(f"{game["title"].lower()} {" ".join(game["genres"].lower().split("|"))} {desc}")

        tokens = [token.lemma_ for token in doc
                if token.pos_ in {"NOUN", "PROPN", "ADJ", "VERB"} 
                    and token.lemma_ not in {"roblox", "game"}
                    and len(token.lemma_) >= 3
                    and not token.like_url
                    and not token.like_email
                    and not token.like_num]

        return " ".join(dict.fromkeys(tokens))

    from sentence_transformers import SentenceTransformer, util
    model = SentenceTransformer("all-MiniLM-L6-v2")

    nth = 73-2
    k = 10

    v = model.encode([__lemmatize(game) for game in games])
    similarities = util.cos_sim(v[nth], v)[0]
    ranks = sorted(zip(similarities, [game["title"] for game in games]), key=lambda x: x[0], reverse=True)[1:k+1]

    print(f"games similar to '{games[nth]["title"]}':")
    for rank in ranks:
        print(rank, len(ranks))
