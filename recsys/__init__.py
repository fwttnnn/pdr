import spacy

__nlp = spacy.load("en_core_web_sm")

def lemmatize(text: str):
    doc = __nlp(text)
    return doc
