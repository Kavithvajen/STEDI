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
    nlp = spacy.load("en_core_web_lg")

    issue_tokens = ['accent', 'address', 'advertisement', 'age', 'behaviour', 'birthday', 'body', 'browser',
            'city', 'colour', 'community', 'consult', 'contact', 'criminal', 'dialect', 'disability', 'doctor',
            'email', 'gender', 'hair', 'health', 'height', 'history', 'immigrant', 'income', 'jail', 'language',
            'loan', 'location', 'medical', 'myers', 'name', 'opinion', 'personality', 'phone', 'piercings',
            'politics', 'race', 'religion', 'resident', 'salary', 'search', 'size', 'skin', 'tattoos','tracking',
            'weight']

    ethics_ontology_dictionary = {"hasAge": False, "hasBehaviourData": False, "hasBodyStatistics": False,
            "isChild": False, "hasContactInformation": False, "hasCriminalActivity": False,
            "hasDataControllerName": False, "hasDoctorConsultationsData": False, "hasEthnicityData": False,
            "hasFilesWithPIIAttached": False, "hasHealthData": False, "hasIncomeData": False,
            "hasLoanRecords": False, "hasLocationData": False, "hasName": False, "hasSignedNDA": False,
            "hasPhysicalCharacteristics": False, "hasPoliticalOpinions": False, "hasReligion": False,
            "hasTooManyDataPoints": False, "hasUserTrackingData": False, "isValidForProcessing": False}

    common_words_to_ignore = ["syntax", "same", "as", "spatial"]

    # Cheekily tried to fit in the mapping of the word lists to the key names of the ethics ontology.
    word_lists = {
        "age_words" : (("age", "birthday", "dob"),
                        "hasAge"),

        "behaviour_words" : (("behaviour", "personality", "myers", "opinion"),
                        "hasBehaviourData"),

        "body_words" : (("body", "height", "weight", "size"),
                        "hasBodyStatistics"),

        "contact_words" : (("contact", "phone", "email"),
                        "hasContactInformation"),

        "criminal_words" : (("criminal", "jail"),
                        "hasCriminalActivity"),

        "doctor_words" : (("doctor", "consult"),
                        "hasDoctorConsultationsData"),

        "ethnic_words" : (("language", "race", "community", "accent", "dialect", "immigrant", "religion"),
                        "hasEthnicityData"),

        "health_words" : (("health", "medical"),
                        "hasHealthData"),

        "income_words" : (("income", "salary"),
                        "hasIncomeData"),

        "loan_words" : (("loan"),
                        "hasLoanRecords"),

        "location_words" : (("address", "city", "location", "resident"),
                        "hasLocationData"),

        "name_words" : (("name"),
                        "hasName"),

        "physical_words" : (("gender", "disability", "colour", "skin", "hair", "tattoos", "piercings"),
                        "hasPhysicalCharacteristics"),

        "politics_words" : (("politics"),
                        "hasPoliticalOpinions"),

        "religion_words" : (("religion"),
                        "hasReligion"),

        "tracking_words" : (("advertisement", "history", "browser", "search", "tracking"),
                        "hasUserTrackingData")
    }

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
                            # A complex shorthand but saves a lot of if-else conditions.
                            # It basically searches for the issue in every tuple in the word_lists dictionary.
                            # It also assigns the appropriate key names of the ethics ontology dictionary.
                            data_property = [word_tuple[1] for word_tuple in word_lists.values() if issue in word_tuple[0]][0]
                            ethics_ontology_dictionary[data_property] = True

    return ethics_ontology_dictionary

def fill_ethics_ontology(dataset_name, ethics_ontology, ethics_ontology_dictionary):
    #Ethics Ontology Namespace
    EONS = rdflib.Namespace("https://www.scss.tcd.ie/~kamarajk/EthicsOntology#")

    #Cleaning up dataset_name so the individuals of the ethics ontology follow a consistent naming convention.
    dataset_name = dataset_name.split('.')[0]
    dataset_name = re.sub("[^A-Za-z0-9 ]+", " ", dataset_name)
    dataset_name = re.sub("[ ]+", " ", dataset_name)
    dataset_name = dataset_name.replace(" ", "_")

    #Creates a named individual with the name of the dataset
    ethics_ontology.add((EONS[dataset_name], RDF.type, OWL.NamedIndividual))

    for key, value in ethics_ontology_dictionary.items():
        ethics_ontology.add((EONS[dataset_name], EONS[key], rdflib.term.Literal(value)))

    return ethics_ontology

def integration_issues():
    pass

def start_execution():
    # Importing the ethics ontology
    ethics_ontology = rdflib.Graph()
    ethics_ontology.parse("Ontology/EthicsOntology.owl", format = rdflib.util.guess_format('/Ontology/EthicsOntology.owl'))

    # Importing the input datasets
    dataset_list = [f for f in os.listdir("Input") if not f.startswith(".")]
    graph_list = []
    for dataset in dataset_list:
        graph_list.append(rdflib.Graph())
        graph_list[-1].parse(f"Input/{dataset}", format = rdflib.util.guess_format(f"/Input/{dataset}"))
        graph_list[-1].serialize(format="xml")
        print("\nSuccessfully loaded the \"{}\" dataset. \nNow checking the vocabulary used in the dataset to find potential issues.".format(dataset))
        for vocab in graph_list[-1].namespace_manager.namespaces():
            check_vocab(vocab[0])

        print("\n\nCHECKING FOR POSSIBLE ETHICAL ISSUES IN THE PREDICATES!\n\n")
        ethics_ontology_dictionary = predicate_issues(graph_list[-1])

        ethics_ontology = fill_ethics_ontology(dataset, ethics_ontology, ethics_ontology_dictionary)

    ethics_ontology.serialize(destination='Output/Updated_Ethics_Ontology.owl', format='xml')
    print("Output - Updated Ethics Ontology created")

    # integration_issues()

def main():
    #The following line is to suppress a common warning message by the rdflib package.
    logging.getLogger("rdflib").setLevel(logging.ERROR)

    option = input("\nStarted the tool successfully.\nAre all the input datasets in the \"Input\" folder? [Y/N]: ")
    if option == "Y" or option == "y":
        start_execution()
    elif option == "N" or option == "n":
        print("\nOkay! Make sure all the input datasets are in the \"Input\" folder and then start the tool.")
        sys.exit()
    else:
        print("Wrong option. Aborting program!")
        sys.exit()

    print("\nTool finished running.")

if __name__ == "__main__":
    main()
