import rdflib
import sys
import os
import re
import spacy

def loadDatasets():
    os.chdir("Input")
    nlp = spacy.load("en_core_web_lg")
    dataset = "TestDataset.owl"
    #dataset = "testDataset.rdf"
    g = rdflib.Graph()
    print("Starting to parse!")
    g.parse(dataset, format = rdflib.util.guess_format("/"+dataset))
    print("Done parsing!")

    for s, p, o in g:
        print(f"\n\nSubject: {s} \n Predicate: {p} \n Object: {o}")

        predicate = p.split("/")
        predicate = predicate[-1]
        predicate = re.sub("[^A-Za-z0-9 ]+", " ", predicate)
        predicate = re.sub(r"([A-Z])", r" \1", predicate)

        print(f"Actual Predicate: {predicate}")

        tokens = nlp(predicate)
        base_token = nlp("gender")

        for token in tokens:
            print(f"Token similarity to 'gender': {token.text} - {token.similarity(base_token)}")

if __name__ == "__main__":
    loadDatasets()
