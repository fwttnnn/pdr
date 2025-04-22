import spacy
import re
from sentence_transformers import SentenceTransformer, util

__nlp: spacy.Language        = None
__model: SentenceTransformer = None

def __nlp_load():
    global __nlp
    __nlp = spacy.load("en_core_web_sm")

def lemmatize(game: dict[str, str]) -> str:
    if not __nlp:
        __nlp_load()

    desc = re.sub(r"\\n", r"\n", game["description"].lower())
    doc = __nlp(f"{game["title"].lower()} {" ".join(game["genres"].lower().split("|"))} {desc}")

    tokens = [token.lemma_ for token in doc
            if token.pos_ in {"NOUN", "PROPN", "ADJ", "VERB"} 
                and token.lemma_ not in {"roblox", "game"}
                and len(token.lemma_) >= 3
                and not token.like_url
                and not token.like_email
                and not token.like_num]

    return " ".join(dict.fromkeys(tokens))

def __model_load():
    global __model
    __model = SentenceTransformer("all-MiniLM-L6-v2")

def similar(games: list[list[dict[str, str]]], nth: int, k: int = 10) -> list[str]:
    if not __model:
        __model_load()

    embeddings = __model.encode([lemmatize(game) for game in games])
    similarities = util.cos_sim(embeddings[nth], embeddings)[0]
    return sorted(zip(similarities, [game["title"] for game in games]), key=lambda x: x[0], reverse=True)[1:k+1]
