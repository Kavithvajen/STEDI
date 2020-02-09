import rdflib
import requests
import sys
import json
import logging

def checkVocab(vocab):
    URL = "https://lov.linkeddata.es/dataset/lov/api/v2/vocabulary/info?"
    PARAMS = {"vocab" : vocab}

    try:
        response = requests.get(url = URL, params = PARAMS)
        data = response.json()

    except requests.exceptions.RequestException as e:
        print("\nAborting due to network issue. Here's the error message: " + e)
        sys.exit()

    except json.decoder.JSONDecodeError:
        return

    for tag in data["tags"]:
        if tag == "Geography":
            print("\nNOTE: This dataset probably contains location related data as it uses the {} namespace!".format(data["prefix"]))

def main():

    #The following line is to suppress a common warning message by the rdflib package.
    logging.getLogger("rdflib").setLevel(logging.ERROR)

    print("\nStarted the tool successfully. Now going to load the dataset.")

    g = rdflib.Graph()
    g.parse("COLINDA.rdf", format = rdflib.util.guess_format("/COLINDA.rdf"))

    print("\nSuccessfully loaded the dataset. Now checking the vocabulary used in the dataset to find potential issues.")

    for vocab in g.namespace_manager.namespaces():
        checkVocab(vocab[0])

    print("\nTool finished running.")

if __name__ == "__main__":
    main()
