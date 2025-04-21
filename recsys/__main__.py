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
    game  = games[2-2]

    desc = re.sub(r"\\n", r"\n", game["description"].lower())

    doc = recsys.lemmatize(f"{game["title"].lower()} {desc}")
    tokens = [token.lemma_ for token in doc
              if token.pos_ in {"NOUN", "PROPN", "ADJ", "VERB"} 
                 and len(token.lemma_) >= 3
                 and not token.like_url
                 and not token.like_email
                 and not token.like_num]
    print(" ".join(dict.fromkeys(tokens)))

