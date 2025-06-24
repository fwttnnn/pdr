#!/usr/bin/env python

"""
Preprocess descriptions with LLaMA 3.2
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).absolute().parent.parent))

import concurrent.futures
import re
import requests
import dataset

OLLAMA_BASE_API_URL = "http://localhost:11434"
CSV_LLAMA_GAMES_PATH = "data/games-llama3.csv"

def transform(desc: str) -> str:
    return requests.post(f"{OLLAMA_BASE_API_URL}/api/generate", json={
        "model": "llama3.2",
        "prompt": f"""
Summarize the following game description as if you are a professional game developer OR game maker.
Use any useful information like how the game is inspired, how the controls describe the game. If none, then don't bother to describe them.

NOTE: If the description is empty, return nothing.
Do not complain or ask, your job is only to summarize into one or several concise and easy to understand paragraphs, the less the better.

Here is the description (good luck, LLaMA the summarizer):
{desc}
""".strip(),
        "stream": False,
    }).json()["response"]

if __name__ == "__main__":
    dataset.load()

    games: dict = {}
    for game in dataset.load_csv(CSV_LLAMA_GAMES_PATH):
        game["id"] = int(game["id"])
        games[game["id"]] = game

    def batch(lst: list, n: int) -> list[list]:
        return [lst[i:i + n] for i in range(0, len(lst), n)]

    def __apply_transform(game: dict):
        games[game["id"]] = game
        games[game["id"]]["genres"] = "|".join(games[game["id"]]["genres"])
        games[game["id"]]["description"] = re.sub(r"\r?\n", r"\\n", transform(game["description"]) or "")

    for chunk in batch([game for game in dataset.games.values() if game["id"] not in games], 10):
        print(f"LLaMA.py: Starting batch")
        print(f"LLaMA.py: {[g['id'] for g in chunk]}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(__apply_transform, chunk)
        
        print(f"LLaMA.py: Checkpoint reached, saving games..")
        dataset.dump_csv(CSV_LLAMA_GAMES_PATH,
                [{"id":           g["id"],
                  "rpid":         g["rpid"],
                  "title":        g["title"],
                  "description":  g["description"],
                  "genres":       g["genres"],
                  "visits":       g["visits"],
                  "favorite":     g["favorite"]} for g in games.values()],
                  ["id", "rpid", "title", "description", "genres", "visits", "favorite"])

    print(f"LLaMA.py: Cleared all, saving games..")
    dataset.dump_csv(CSV_LLAMA_GAMES_PATH,
            [{"id":           g["id"],
              "rpid":         g["rpid"],
              "title":        g["title"],
              "description":  g["description"],
              "genres":       g["genres"],
              "visits":       g["visits"],
              "favorite":     g["favorite"]} for g in games.values()],
              ["id", "rpid", "title", "description", "genres", "visits", "favorite"])
