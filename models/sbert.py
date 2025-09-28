from sentence_transformers import SentenceTransformer
import torch

# all-MiniLM-L6-v2 | all-mpnet-base-v2 | all-distilroberta-v1 | distiluse-base-multilingual-cased-v2
sbert: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")

def __encode(text: str) -> torch.Tensor:
    return sbert.encode(text, convert_to_tensor=True)
