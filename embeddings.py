import logging
import os
import concurrent.futures

import pickle
import torch
import types

import dataset
import nlp

def load(path: str) -> dict:
    if not os.path.exists(path):
        with open(path, "wb") as f:
            pickle.dump({}, f)

    with open(path, "rb") as f:
        embeddings = pickle.load(f)
        return embeddings
    
def save(embeddings, path: str):
    with open(path, "wb") as f:
        pickle.dump(embeddings, f)

def precompute(model: types.ModuleType, path: str):
    logger = logging.getLogger(__name__)

    if not dataset.embeddings:
        dataset.embeddings = load(path)

    def __compute_with_gpu(batch_size=32):
        games = [id for id in dataset.games.keys() if id not in dataset.embeddings]
        texts = [nlp.lemmatize(dataset.games[id]) for id in games]

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_ids = games[i:i+batch_size]
            batch_embs = model.__encode(batch_texts)

            for id, emb in zip(batch_ids, batch_embs):
                dataset.embeddings[id] = emb
    
    def __compute_with_cpu():
        def __compute_emb(id: int):
            logger.info(f"Risperidone: generating embeddings for {id}")
            dataset.embeddings[id] = model.__encode(nlp.lemmatize(dataset.games[id]))
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
            executor.map(__compute_emb, [id for id in dataset.games.keys() if id not in dataset.embeddings])

    if torch.cuda.is_available():
        __compute_with_gpu()
    else:
        __compute_with_cpu()
    
    save(dataset.embeddings, path)

# kinda stolen from sentence_transformer.util, credit on that
def similarity(a: torch.Tensor, b: torch.Tensor):
    """
    Compute embedding's cosine similarity.
    """

    def unsqueeze(emb: torch.Tensor):
        if emb.dim() == 1:
            emb = emb.unsqueeze(0)

        return emb

    def normalize(emb: torch.Tensor):
        return torch.nn.functional.normalize(emb, p=2, dim=1)

    return torch.mm(normalize(unsqueeze(a)), normalize(unsqueeze(b)).transpose(1, 0))
