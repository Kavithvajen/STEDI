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

def predicate_issues(graph):
    #os.chdir("Input")
    nlp = spacy.load("en_core_web_lg")

    for p in graph.predicates():
        predicate_parts = p.split("/")
        predicate = predicate_parts[-1]
        predicate = re.sub("[^A-Za-z0-9 ]+", " ", predicate)
        predicate = re.sub(r"([A-Z])", r" \1", predicate)
        predicate = predicate.lower()

        predicate_tokens = nlp(predicate)
        issue_tokens = ["gender", "age", "behaviour", "personality", "myers", "body",
            "contact", "phone", "email", "criminal", "birthday", "doctor", "name",
            "health", "salary", "loan", "location", "address", "history", "search",
            "resident", "city", "characteristics", "politics", "opinion",
            "religion", "language", "race", "community", "sexual", "tracking",
            "advertisement"]

        ethics_ontology = {"age": False, "behaviour": False, "body": False, "contact": False,
            "criminal": False, "dob": False, "doctor": False, "ethic": False, "files": False,
            "health": False, "income": False, "loan": False, "location": False, "name": False,
            "physical": False, "politics": False, "religion": False, "sexual": False, "nda": False,
            "data_controller": False, "too_much_data": False, "tracking": False, "child": False,
            "valid_processing": False}

        common_words_to_ignore = ["syntax", "same", "as", "spatial"]

        for token in predicate_tokens:
            if token.text in common_words_to_ignore:
                continue
            else:
                for issue in issue_tokens:
                    # To avoid checking similarity for empty vectors.
                    if token.has_vector and token.similarity(nlp(issue)) > 0.5:
                            print(f"Contains {issue} related data! -> {token}")

def integration_issues():
    pass

def start_execution():
    os.chdir("Input")
    dataset_list = [f for f in os.listdir() if not f.startswith('.')]
    graph_list = []
    for dataset in dataset_list:
        graph_list.append(rdflib.Graph())
        graph_list[-1].parse(dataset, format = rdflib.util.guess_format(f"/{dataset}"))
        graph_list[-1].serialize(format="xml")
        print("\nSuccessfully loaded the \"{}\" dataset. \nNow checking the vocabulary used in the dataset to find potential issues.".format(dataset))
        for vocab in graph_list[-1].namespace_manager.namespaces():
            check_vocab(vocab[0])

        print("\n\nCHECKING FOR POSSIBLE ETHICAL ISSUES IN THE PREDICATES!\n\n")
        predicate_issues(graph_list[-1])

    integration_issues()

def main():
    #The following line is to suppress a common warning message by the rdflib package.
    logging.getLogger("rdflib").setLevel(logging.ERROR)

    option = input("\nStarted the tool successfully.\nAre all the input datasets in the \"Input\" folder? [Y/N]: ")
    if option == "Y" or option == "y":
        start_execution()
    elif option == "N" or option == "n":
        print("Okay! Make sure all the input datasets are in the \"Input\" folder and then start the tool.")
        sys.exit()
    else:
        print("Wrong option. Aborting program!")
        sys.exit()

    print("\nTool finished running.")

if __name__ == "__main__":
    main()
