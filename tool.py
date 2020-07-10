import rdflib
from rdflib.namespace import RDF, OWL
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

    issue_tokens = ['accent', 'address', 'advertisement', 'age', 'behaviour', 'birthday', 'body', 'browser',
            'city', 'colour', 'community', 'consult', 'contact', 'criminal', 'dialect', 'disability', 'doctor',
            'email', 'gender', 'hair', 'health', 'height', 'history', 'immigrant', 'income', 'jail', 'language',
            'loan', 'location', 'medical', 'myers', 'name', 'opinion', 'personality', 'phone', 'piercings',
            'politics', 'race', 'religion', 'resident', 'salary', 'search', 'size', 'skin', 'tattoos','tracking',
            'weight']

    ethics_ontology_issues = {"age": False, "behaviour": False, "body": False, "child": False, "contact": False,
            "criminal": False, "data_controller": False, "dob": False, "doctor": False, "ethnic": False,
            "files": False, "health": False, "income": False, "loan": False, "location": False, "name": False,
            "nda": False, "physical": False, "politics": False, "religion": False, "too_much_data": False,
            "tracking": False, "valid_processing": False}

    common_words_to_ignore = ["syntax", "same", "as", "spatial"]

    age_words = ["age", "birthday"]
    behaviour_words = ["behaviour", "personality", "myers", "opinion"]
    body_words = ["body", "height", "weight", "size"]
    contact_words = ["contact", "phone", "email"]
    criminal_words = ["criminal", "jail"]
    doctor_words = ["doctor", "consult"]
    ethnic_words = ["language", "race", "community", "accent", "dialect", "immigrant", "religion"]
    health_words = ["health", "medical"]
    income_words = ["income", "salary"]
    loan_words = ["loan"]
    location_words = ["address", "city", "location", "resident"]
    name_words = ["name"]
    physical_words = ["gender", "disability", "colour", "skin", "hair", "tattoos", "piercings"]
    politics_words = ["politics"]
    religion_words = ["religion"]
    tracking_words = ["advertisement", "history", "browser", "search", "tracking"]

    for p in graph.predicates():
        predicate_parts = p.split("/")
        predicate = predicate_parts[-1]
        predicate = re.sub("[^A-Za-z0-9 ]+", " ", predicate)
        predicate = re.sub(r"([A-Z])", r" \1", predicate)
        predicate = predicate.lower()

        predicate_tokens = nlp(predicate)

        for token in predicate_tokens:
            if token.text in common_words_to_ignore:
                continue
            else:
                for issue in issue_tokens:
                    # To avoid checking similarity for empty vectors.
                    if token.has_vector and token.similarity(nlp(issue)) > 0.5:
                            print(f"Contains {issue} related data! -> {token}")
                            if issue in age_words:
                                ethics_ontology_issues["age"] = True
                                ethics_ontology_issues["dob"] = True
                            elif issue in behaviour_words:
                                ethics_ontology_issues["behaviour"] = True
                            elif issue in body_words:
                                ethics_ontology_issues["body"] = True
                            elif issue in contact_words:
                                ethics_ontology_issues["contact"] = True
                            elif issue in criminal_words:
                                ethics_ontology_issues["criminal"] = True
                            elif issue in doctor_words:
                                ethics_ontology_issues["doctor"] = True
                            elif issue in ethnic_words:
                                ethics_ontology_issues["ethnic"] = True
                            elif issue in health_words:
                                ethics_ontology_issues["health"] = True
                            elif issue in income_words:
                                ethics_ontology_issues["income"] = True
                            elif issue in loan_words:
                                ethics_ontology_issues["loan"] = True
                            elif issue in location_words:
                                ethics_ontology_issues["location"] = True
                            elif issue in name_words:
                                ethics_ontology_issues["name"] = True
                            elif issue in physical_words:
                                ethics_ontology_issues["physical"] = True
                            elif issue in politics_words:
                                ethics_ontology_issues["politics"] = True
                            elif issue in religion_words:
                                ethics_ontology_issues["religion"] = True
                            elif issue in tracking_words:
                                ethics_ontology_issues["tracking"] = True
                            else:
                                print("We may have a problem!")

    print(f"\nEthics Ontology Issues Dictionary: \n {ethics_ontology_issues}\n")

def fill_ethics_ontology():
    pass

def integration_issues():
    pass

def start_execution():
    os.chdir("Input")
    dataset_list = [f for f in os.listdir() if not f.startswith(".")]
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
