import rdflib
from rdflib.namespace import RDF, OWL
import requests
import json
import sys
import os
import logging
import spacy
import re

def questionnaire(organisation_name, dataset, ethics_ontology_dictionary):

    # To check if the data subject has provided the data controller consent to process their data.
    data_controller = input("\nEnter the name of the data controller that the data subject originally agreed to share their data with: ")
    if organisation_name == data_controller:
        ethics_ontology_dictionary["isValidForProcessing"] = True

    # To check if any PII is present in attached files.
    attached_files = input("Are there any files attached in this database? \n[Reply with keywords describing the file or N (for NO FILES ATTACHED)]: ")
    if attached_files != "N" and attached_files != "n":
        file_name = input("Enter name of file or keyword(s) describing the file (E.g: \"resume\"): ")
        nlp = spacy.load("en_core_web_lg")

        issue_tokens = ["resume, photo, scan, finance, doctor, personal, certificate, proof"]

        file_name = file_name.lower()
        file_name = re.sub("[^a-z ]+", " ", file_name)

        file_name_tokens = nlp(file_name)

        for token in file_name_tokens:
            for issue in issue_tokens:
                # To avoid checking similarity for empty vectors.
                if token.has_vector and token.similarity(nlp(issue)) > 0.5:
                        print(f"File name has {issue} issue! -> {token}")
                        ethics_ontology_dictionary["hasFilesWithPIIAttached"] == True

    # To identify the data subject type.
    while True:
        data_subject = input("Are the data subjects individuals or groups? [I/G]: ")
        if data_subject == "I" or data_subject == "i":
            ethics_ontology_dictionary["representsIndividuals"] = True
            break
        elif data_subject == "G" or data_subject == "g":
            ethics_ontology_dictionary["representsGroups"] = True
            break
        else:
            print(f"{data_subject} is invalid input. Try again!\n")

    # If the dataset represents individuals then the following questions need to be answered.
    if data_subject == "I" or data_subject == "i":
        while True:
            child_status = input("Could any of the individuals in the dataset be children? [Y/N]: ")
            if child_status == "Y" or child_status == "y":
                ethics_ontology_dictionary["isChild"] == True
                break
            elif child_status == "N" or child_status == "n":
                break
            else:
                print(f"{child_status} is invalid input. Try again!\n")

        while True:
            nda_status = input("Have the individuals signed a non-disclosure agreement (NDA) [Y/N]: ")
            if nda_status == "Y" or nda_status == "y":
                ethics_ontology_dictionary["hasSignedNDA"] == True
                break
            elif nda_status == "N" or nda_status == "n":
                break
            else:
                print(f"{nda_status} is invalid input. Try again!\n")

    return ethics_ontology_dictionary

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

def predicate_issues(graph, ethics_ontology_dictionary):
    nlp = spacy.load("en_core_web_lg")

    issue_tokens = ['accent', 'address', 'advertisement', 'age', 'behaviour', 'birthday', 'body', 'browser',
            'city', 'colour', 'community', 'consult', 'contact', 'criminal', 'dialect', 'disability', 'doctor',
            'email', 'gender', 'hair', 'health', 'height', 'history', 'immigrant', 'income', 'jail', 'language',
            'loan', 'location', 'medical', 'myers', 'name', 'opinion', 'personality', 'phone', 'piercings',
            'politics', 'race', 'religion', 'resident', 'salary', 'search', 'size', 'skin', 'tattoos','tracking',
            'weight']

    common_words_to_ignore = ["syntax", "same", "as", "spatial"]

    # Cheekily tried to fit in the mapping of the word lists to the key names of the ethics ontology.
    # Using list inside of the tuple to keep the list of words as an iterable objects when unpacking the tuple.
    # If it were a tuple inside a tuple, then when only a single object (name, politics, etc) is present, the word
    # itself will be iterated upon. Thereby loosing meaning and only a bunch of characters will be present.
    word_lists = {
        "age_words" : (["age", "birthday", "dob"],
                        "hasAge"),

        "behaviour_words" : (["behaviour", "personality", "myers", "opinion"],
                        "hasBehaviourData"),

        "contact_words" : (["contact", "phone", "email"],
                        "hasContactInformation"),

        "criminal_words" : (["criminal", "jail"],
                        "hasCriminalActivity"),

        "ethnic_words" : (["language", "race", "community", "accent", "dialect", "immigrant", "religion"],
                        "hasEthnicityData"),

        "health_words" : (["health", "medical", "doctor", "consult"],
                        "hasHealthData"),

        "income_words" : (["income", "salary"],
                        "hasIncomeData"),

        "loan_words" : (["loan"],
                        "hasLoanRecords"),

        "location_words" : (["address", "city", "location", "resident"],
                        "hasLocationData"),

        "name_words" : (["name"],
                        "hasName"),

        "physical_words" : (["gender", "disability", "colour", "skin", "hair", "tattoos", "piercings",
                        "body", "height", "weight", "size"],
                        "hasPhysicalCharacteristics"),

        "politics_words" : (["politics"],
                        "hasPoliticalOpinions"),

        "religion_words" : (["religion"],
                        "hasReligion"),

        "tracking_words" : (["advertisement", "history", "browser", "search", "tracking"],
                        "hasUserTrackingData")
    }

    for p in graph.predicates():
        predicate_parts = p.split("/")
        predicate = predicate_parts[-1]
        predicate = re.sub("[^A-Za-z0-9 ]+", " ", predicate)
        # To split camel case
        predicate = re.sub(r"([A-Z])", r" \1", predicate)
        predicate = predicate.lower()

        predicate_tokens = nlp(predicate)

        for token in predicate_tokens:
            if token.text in common_words_to_ignore:
                continue
            else:
                #for issue in issue_tokens: OLD METHOD. Now retiring it for code refactoring.
                for word_list in word_lists.values():
                    for issue in word_list[0]:
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

def start_execution(organisation_name):
    # Importing the ethics ontology
    ethics_ontology = rdflib.Graph()
    ethics_ontology.parse("Ontology/EthicsOntology.owl", format = rdflib.util.guess_format('/Ontology/EthicsOntology.owl'))

    # Importing the input datasets
    dataset_list = [f for f in os.listdir("Input") if not f.startswith(".")]
    graph_list = []
    ctr = 1

    for dataset in dataset_list:
        ethics_ontology_dictionary = {"hasAge": False, "hasBehaviourData": False, "hasContactInformation": False,
        "hasCriminalActivity": False, "hasDataControllerName": False, "hasEthnicityData": False,
        "hasFilesWithPIIAttached": False, "hasHealthData": False, "hasIncomeData": False, "hasLoanRecords": False,
        "hasLocationData": False, "hasName": False, "hasPhysicalCharacteristics": False, "hasPoliticalOpinions": False,
        "hasReligion": False, "hasSignedNDA": False,"hasTooManyDataPoints": False, "hasUserTrackingData": False,
        "isChild": False, "isValidForProcessing": False, "representsGroups": False, "representsIndividuals": True}

        graph_list.append(rdflib.Graph())
        graph_list[-1].parse(f"Input/{dataset}", format = rdflib.util.guess_format(f"/Input/{dataset}"))
        graph_list[-1].serialize(format="xml")
        print(f"\nSUCCESSFULLY LOADED DATASET - {ctr} : {dataset}")

        print(f"\n* Please answer the following questionnaire about dataset - {ctr}: ")
        ethics_ontology_dictionary = questionnaire(organisation_name, dataset, ethics_ontology_dictionary)

        print(f"\n* Checking the vocabulary used in dataset - {ctr} for potential ethics issues.")

        for vocab in graph_list[-1].namespace_manager.namespaces():
            check_vocab(vocab[0])

        print(f"\n* Checking for possbile ethical issues in the predicates of dataset - {ctr}")
        ethics_ontology_dictionary = predicate_issues(graph_list[-1], ethics_ontology_dictionary)

        ethics_ontology = fill_ethics_ontology(dataset, ethics_ontology, ethics_ontology_dictionary)
        print(f"\nDONE PROCESSING DATASET - {ctr}: {dataset}\n")
        ctr += 1


    ethics_ontology.serialize(destination='Output/Updated_Ethics_Ontology.owl', format='xml')
    print("\nOutput - Updated Ethics Ontology created")

    # integration_issues()

def main():
    #The following line is to suppress a common warning message by the rdflib package.
    logging.getLogger("rdflib").setLevel(logging.ERROR)

    option = input("\nStarted the tool successfully.\nAre all the input datasets in the \"Input\" folder? [Y/N]: ")
    if option == "Y" or option == "y":
        organisation_name = input("\nPlease input the name of your organisation: ")
        start_execution(organisation_name)
    elif option == "N" or option == "n":
        print("\nOkay! Make sure all the input datasets are in the \"Input\" folder and then start the tool.")
        sys.exit()
    else:
        print("Wrong option. Aborting program!")
        sys.exit()

    print("\nTool finished running.")

if __name__ == "__main__":
    main()
