import recsys.nlp

import sentence_transformers.util
from sentence_transformers import SentenceTransformer

__model: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")

def similar(games: list[dict[str, str]], nth: int, k: int = 10) -> list[str]:
    embeddings = __model.encode([recsys.nlp.lemmatize(game) for game in games])
    similarities = sentence_transformers.util.cos_sim(embeddings[nth], embeddings)[0]
    return sorted(zip(similarities, [game["title"] for game in games]), key=lambda x: x[0], reverse=True)[1:k+1]
