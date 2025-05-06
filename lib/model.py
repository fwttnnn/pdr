import dataset
import nlp

import torch
import sentence_transformers.util
from sentence_transformers import SentenceTransformer

# all-MiniLM-L6-v2 | all-mpnet-base-v2
__model: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")

def __pre_compute_embeddings():
    for id, embedding in dataset.__load_embeddings().items():
        dataset.__games[id]["__embed"] = embedding

    added = False
    for game in dataset.__games.values():
        if "__embed" in game:
            continue
        
        added = True
        game["__embed"] = __model.encode(nlp.lemmatize(game), convert_to_tensor=True)

    if added:
        dataset.__save_embeddings()

dataset.__load()
__pre_compute_embeddings()

def similar(game_ids: list[int], k: int = 10) -> list[tuple]:
    predictions: list[tuple] = []

    game_ids = set(game_ids)
    embeddings = [game["__embed"] for game in dataset.__games.values() if game["id"] in game_ids]

    for game in dataset.__games.values():
        if game["id"] in game_ids:
            continue

        similarities = [sentence_transformers.util.cos_sim(embedding, game["__embed"]).item() for embedding in embeddings]
        predictions.append((torch.mean(torch.tensor(similarities)), game["id"]))
    
    # TODO: we should use sorted list
    return sorted(predictions, key=lambda x: x[0], reverse=True)[:k]
