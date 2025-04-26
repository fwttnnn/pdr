import spacy
import re

__nlp: spacy.Language = spacy.load("en_core_web_sm")

def lemmatize(game: dict[str, str]) -> str:
    desc = re.sub(r"\\n", r"\n", game["description"].lower())
    doc = __nlp(f"{game["title"].lower()} {" ".join(game["genres"].lower().split("|"))} {desc}")

    tokens = [token.lemma_ for token in doc
            if token.pos_ in {"NOUN", "PROPN", "ADJ", "VERB"} 
                and len(token.lemma_) >= 3
                and not token.like_url
                and not token.like_email
                and not token.like_num]

    return " ".join(tokens)
