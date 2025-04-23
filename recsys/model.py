import recsys.dataset
import recsys.nlp

import sentence_transformers.util
from sentence_transformers import SentenceTransformer

__model: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")

def __pre_compute_embeddings():
    for game in recsys.dataset.__dataset.values():
        if "__embed" in game:
            continue
        
        game["__embed"] = __model.encode(recsys.nlp.lemmatize(game))

def similar(game_id: int, k: int = 10) -> list[str]:
    __pre_compute_embeddings()

    similarities: list[tuple] = []
    for game in recsys.dataset.__dataset.values():
        similarity = sentence_transformers.util.cos_sim(recsys.dataset.__dataset[game_id]["__embed"], game["__embed"])[0][0]
        similarities.append((similarity, game["title"]))
    
    # TODO: we should use sorted list
    return sorted(similarities, key=lambda x: x[0], reverse=True)[1:k+1]
