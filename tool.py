import rdflib
import requests
import json
import sys
import os
import logging
import spacy
import re

def check_vocab(vocab):
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

    sensitive_namespaces = ["Geography", "Society", "People", "Health", "Biology", "Government", "Environment"]

    for tag in data["tags"]:
        for namespace in sensitive_namespaces:
            if tag == namespace:
                print(f"\nNOTE: This dataset probably contains {namespace} related data as it uses the {data['prefix']} namespace!")

def load_datasets():
    os.chdir("Input")
    dataset_list = [f for f in os.listdir() if not f.startswith('.')]
    graph_list = []

    for dataset in dataset_list:
        graph_list.append(rdflib.Graph())
        graph_list[-1].parse(dataset, format = rdflib.util.guess_format("/"+dataset))
        print("\nSuccessfully loaded the \"{}\" dataset. \nNow checking the vocabulary used in the dataset to find potential issues.".format(dataset))
        for vocab in graph_list[-1].namespace_manager.namespaces():
            check_vocab(vocab[0])

def predicate_issues():
    os.chdir("Input")
    nlp = spacy.load("en_core_web_lg")
    dataset = "TestDataset.owl"
    g = rdflib.Graph()
    g.parse(dataset, format = rdflib.util.guess_format("/"+dataset))

    for p in g.predicates():
        predicate_parts = p.split("/")
        predicate = predicate_parts[-1]
        predicate = re.sub("[^A-Za-z0-9 ]+", " ", predicate)
        predicate = re.sub(r"([A-Z])", r" \1", predicate)

        predicate_tokens = nlp(predicate)
        issue_tokens = ["gender", "age", "behaviour", "personality", "myers",
            "body", "contact", "phone", "email", "criminal", "birthday", "doctor",
            "ethnicity", "health", "income", "salary", "loan", "location", "address",
            "resident", "city", "name", "characteristics", "politics", "opinion",
            "religion", "language", "race", "community", "sexuality", "sexual",
            "tracking", "ad", "advertisement"]

        for token in predicate_tokens:
            for issue in issue_tokens:
                if token.similarity(nlp(issue)) > 0.5:
                    print(f"Contains {issue} related data!")

def object_issues(nlp, g):
    for o in g.objects():
        print(f"\nObject: {o}")

def main():
    #The following line is to suppress a common warning message by the rdflib package.
    logging.getLogger("rdflib").setLevel(logging.ERROR)

    option = input("\nStarted the tool successfully.\nAre all the input datasets in the \"Input\" folder? [Y/N]: ")
    if option == "Y" or option == "y":
        load_datasets()
        os.chdir("..")
        predicate_issues()

    elif option == "N" or option == "n":
        print("Okay! Make sure all the input datasets are in the \"Input\" folder and then start the tool.")
        sys.exit()
    else:
        print("Wrong option. Aborting program!")
        sys.exit()

    print("\nTool finished running.")

if __name__ == "__main__":
    main()
