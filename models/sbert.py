from sentence_transformers import SentenceTransformer
import torch

sbert = None

def load():
    global sbert
    # all-MiniLM-L6-v2 | all-mpnet-base-v2 | all-distilroberta-v1 | distiluse-base-multilingual-cased-v2
    sbert = SentenceTransformer("all-MiniLM-L6-v2")
    return sbert

def __encode(t: str | list[str]) -> torch.Tensor:
    return sbert.encode(t, convert_to_tensor=True)
