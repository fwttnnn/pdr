import spacy

def lemmatize(text: str):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    return doc
