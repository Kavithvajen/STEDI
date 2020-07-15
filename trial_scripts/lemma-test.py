import spacy

nlp = spacy.load("en_core_web_lg")

n = nlp("finance")

print(f"n.has_vector: {n.has_vector}")
print(f'n.similarity(nlp("financial")): {n.similarity(nlp("financial"))}')
#if token.has_vector and token.similarity(nlp(issue)) > 0.5:
