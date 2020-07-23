import rdflib
from rdflib.namespace import RDF, RDFS, OWL
import requests
import json
import sys
import os
import logging
import spacy
import re

# Using these global lists for code simplification
yes = ("Y", "y", "yes", "Yes", "YES")
no = ("N", "n", "no", "No", "NO")

# Globally loading the language model to avoid loading it everytime it's used
nlp = spacy.load("en_core_web_md")

class Dataset():

    number_of_datasets = 0
    # To be able to effectively ignore these common predictes and tokens while processing the dataset.
    common_schema_predicates = (RDF.type, RDFS.range, RDFS.domain, RDFS.label, OWL.imports)
    common_words_to_ignore = ["as", "the", "is", "of", "has"]

    def __init__(self, dataset_name):
        Dataset.number_of_datasets += 1
        self.dataset_name = dataset_name
        self.graph = rdflib.Graph()
        self.ethics_ontology_dictionary = {"hasAge": False, "hasBehaviourData": False, "hasContactInformation": False,
        "hasCriminalActivity": False, "hasDataControllerName": False, "hasEthnicityData": False,
        "hasFilesWithPIIAttached": False, "hasHealthData": False, "hasIncomeData": False, "hasLoanRecords": False,
        "hasLocationData": False, "hasName": False, "hasPhysicalCharacteristics": False, "hasPoliticalOpinions": False,
        "hasReligion": False, "hasSignedNDA": False,"hasTooManyDataPoints": False, "hasUserTrackingData": False,
        "hasChildData": False, "isValidForProcessing": False, "representsGroups": False, "representsIndividuals": False}


    def load_dataset(self):
        self.graph.parse(f"input/{self.dataset_name}", format=rdflib.util.guess_format(f"/input/{self.dataset_name}"))
        self.graph.serialize(format="xml")
        print(f"\nSUCCESSFULLY LOADED DATASET - {Dataset.number_of_datasets}: {self.dataset_name}\n")


    def predicate_processor(self, word_lists_dict):
        for p in self.graph.predicates():
            if p not in Dataset.common_schema_predicates:
                predicate_parts = p.split("/")
                predicate = predicate_parts[-1]
                predicate = re.sub("[^A-Za-z0-9 ]+", " ", predicate)
                # To split camel case
                predicate = re.sub(r"([A-Z])", r" \1", predicate)
                predicate = predicate.lower()

                predicate_tokens = nlp(predicate)

                for token in predicate_tokens:
                    if token.text not in Dataset.common_words_to_ignore:
                        for word_list in word_lists_dict.values():
                            for issue in word_list[0]:
                                # 1st condition checks if its the same thing, this eliminates the unnecessary use of NLP.
                                # 2nd condition avoids checking similarity for empty vectors first and then does the similarity check.
                                # "0.5" allowed a wider range of words to creep in as issues, so after trial and error I settled on "0.6".
                                if (str(token).lower() == issue.lower()) or (token.has_vector and token.similarity(nlp(issue)) > 0.6) :
                                    data_property = [word_list[1]][0]
                                    # print(f"Token : {str(token)} | Issue : {issue} | Property : {data_property}")
                                    self.ethics_ontology_dictionary[data_property] = True


    def check_individual_specific_issues(self):
        # Checking if any individual in the dataset has too many data points.
        subjects = []
        for s in self.graph.subjects():
            if s not in subjects:
                subjects.append(s)

        for s in subjects:
            no_of_data_points = 0
            for p in self.graph.predicates(subject=s):
                if p not in Dataset.common_schema_predicates:
                    no_of_data_points += 1
            # No reason why having 10 data points is high.
            # A number can be fixed if extensive research was conducted in this exact area.
            if no_of_data_points >= 10:
                self.ethics_ontology_dictionary["hasTooManyDataPoints"] = True
                break

        # Checking if the individual has signed an NDA, or if their name or contact information is present in the dataset.
        word_lists_dict = {
            "contact_words" : (["contact", "phone", "email", "account", "skype", ],
                            "hasContactInformation"),

            "name_words" : (["name"],
                            "hasName"),

            "nda_words" : (["NDA", "non-disclosure", "nondisclosure", "confidential", "secrecy", "agreement"],
                            "hasSignedNDA")
        }

        self.predicate_processor(word_lists_dict)


    def questionnaire(self, organisation_name):
        # To check if the data subject has provided the data controller consent to process their data.
        print(f"\n* Please answer the following questionnaire about dataset - {self.number_of_datasets}.")
        data_controller = input("\nEnter the name of the data controller that the data subject originally agreed to share their data with: ")
        self.ethics_ontology_dictionary["hasDataControllerName"] = data_controller
        if organisation_name.lower() == data_controller.lower():
            self.ethics_ontology_dictionary["isValidForProcessing"] = True

        # To check if any PII is present in attached files.
        while True:
            attached_files = input("\nAre there any files attached in this database? [Y/N]: ")
            if attached_files in yes:
                file_name = input("\nEnter name of file or keyword(s) describing the file (E.g: \"resume\"): ")
                file_name = file_name.lower()
                file_name = re.sub("[^a-z ]+", " ", file_name)

                issue_tokens = ("resume", "cv","photo", "scan", "finance", "doctor", "personal", "certificate", "proof", "record")

                file_name_tokens = nlp(file_name)

                for token in file_name_tokens:
                    for issue in issue_tokens:
                        # To avoid checking similarity for empty vectors.
                        if token.has_vector and token.similarity(nlp(issue)) > 0.5:
                            self.ethics_ontology_dictionary["hasFilesWithPIIAttached"] = True
                break

            elif attached_files in no:
                break
            else:
                print(f"{attached_files} is an invalid input. Try again!\n")

        # To identify the data subject type.
        while True:
            data_subject = input("\nAre the data subjects individuals or groups? [I/G]: ")
            if data_subject == "I" or data_subject == "i":
                self.ethics_ontology_dictionary["representsIndividuals"] = True
                break
            elif data_subject == "G" or data_subject == "g":
                self.ethics_ontology_dictionary["representsGroups"] = True
                break
            else:
                print(f"{data_subject} is an invalid input. Try again!\n")


    def check_vocab(self):
        print(f"\n* Checking for potential ethics issues in the namespaces used for dataset - {self.number_of_datasets}")

        URL = "https://lov.linkeddata.es/dataset/lov/api/v2/vocabulary/info?"
        network_error = False

        for vocab in self.graph.namespace_manager.namespaces():
            #ethics_ontology_dictionary = check_vocab(vocab[0], ethics_ontology_dictionary)
            #ethics_ontology_dictionary, network_error = check_vocab(vocab[0], ethics_ontology_dictionary)

            PARAMS = {"vocab" : vocab[0]}

            try:
                response = requests.get(url = URL, params = PARAMS)
                response.raise_for_status()
                data = response.json()

            except requests.exceptions.HTTPError as e:
                if response.status_code == 503:
                    print(f"\nThe vocabulary API service is temporarily down. The program will still continue in offline mode!")
                    network_error = True

                elif response.status_code == 404:
                    # This status code is returned when no data is found for the requested namespace.
                    # The program must continue looking for data on other namespaces, that's why we use pass here.
                    pass

                else:
                    print(f"\nThere seems to be some unknown error with the API. The program will still continue in offline mode!\nError message received from server: \n{e}")
                    network_error = True

            except ValueError as e:
                print(f"\nJSON Decoding error. The program will still continue!\nError:\n{e}")

            except Exception as e:
                print(f"\nThere seems to be an unexpected error. Quitting program for now. Copy the error message displayed below and contact the system administrator!\n{e}")
                sys.exit()

            # To stop hitting the unresponsive server again and again!
            finally:
                if network_error:
                    break

            # If no data was found for the namespace (Error 404), then the data dictionary will not exist.
            if "data" in locals():
                sensitive_namespaces = (("Geography", "hasLocationData"), ("Society", "hasEthnicityData"), ("Health", "hasHealthData"), ("Biology", "hasHealthData"), ("Government", "hasPoliticalOpinions"))

                for tag in data["tags"]:
                    for namespace in sensitive_namespaces:
                        if tag == namespace[0]:
                            # print(f"\nNOTE: This dataset probably contains {namespace} related data as it uses the {data['prefix']} namespace!")
                            self.ethics_ontology_dictionary[namespace[1]] = True


    def check_predicate_issues(self):
        print(f"\n* Checking for potential ethics issues in the predicates of dataset - {self.number_of_datasets}")

        # Seperately checking for the individual specific ethics issues
        if self.ethics_ontology_dictionary["representsIndividuals"] == True:
            self.check_individual_specific_issues()

        # Using list inside of the tuple to keep the list of words as an iterable objects when unpacking the tuple.
        # If it were a tuple inside a tuple, then when only a single object (name, politics, etc) is present, the word
        # itself will be iterated upon. Thereby loosing meaning and only a bunch of characters will be present.
        word_lists_dict = {
            "age_words" : (["age", "birthday", "dob"],
                            "hasAge"),

            "behaviour_words" : (["behaviour", "personality", "myers", "opinion"],
                            "hasBehaviourData"),

            "child_words" : (["child", "kid", "baby", "minor", "juvenile", "teenager", "youngster"],
                            "hasChildData"),

            "criminal_words" : (["criminal", "jail"],
                            "hasCriminalActivity"),

            "ethnic_words" : (["language", "race", "community", "accent", "dialect", "immigrant", "religion"],
                            "hasEthnicityData"),

            "health_words" : (["health", "medical", "doctor", "consult", "DNA"],
                            "hasHealthData"),

            "income_words" : (["income", "salary"],
                            "hasIncomeData"),

            "loan_words" : (["loan"],
                            "hasLoanRecords"),

            "location_words" : (["address", "city", "location", "resident", "area", "zip-code", "postal"],
                            "hasLocationData"),

            "physical_words" : (["gender", "disability", "colour", "skin", "hair", "tattoos", "piercings",
                            "body", "height", "weight", "size"],
                            "hasPhysicalCharacteristics"),

            "politics_words" : (["politics"],
                            "hasPoliticalOpinions"),

            "religion_words" : (["religion", "faith", "worship", "divinity"],
                            "hasReligion"),

            "tracking_words" : (["advertisement", "history", "browser", "search", "tracking"],
                            "hasUserTrackingData")
        }

        self.predicate_processor(word_lists_dict)


    def fill_ethics_ontology(self, ethics_ontology):
        print(f"\n* Filling the ethics ontology for dataset - {self.number_of_datasets}")

        # Ethics Ontology Namespace
        EONS = rdflib.Namespace("https://www.scss.tcd.ie/~kamarajk/EthicsOntology#")

        # Cleaning up dataset_name so the individuals of the ethics ontology follow a consistent naming convention.
        dataset_name = self.dataset_name.split('.')[0]
        dataset_name = re.sub("[^A-Za-z0-9 ]+", " ", dataset_name)
        dataset_name = re.sub("[ ]+", " ", dataset_name)
        dataset_name = dataset_name.replace(" ", "_")

        # Creates a named individual with the name of the dataset
        ethics_ontology.add((EONS[dataset_name], RDF.type, OWL.NamedIndividual))

        # Identifying data subject type and removing that data from the dictionary
        if self.ethics_ontology_dictionary["representsIndividuals"] == True:
            ethics_ontology.add((EONS[dataset_name], RDF.type, EONS.Individual))
            del self.ethics_ontology_dictionary["representsIndividuals"]
            del self.ethics_ontology_dictionary["representsGroups"]

        else:
            ethics_ontology.add((EONS[dataset_name], RDF.type, EONS.Group))
            del self.ethics_ontology_dictionary["representsIndividuals"]
            del self.ethics_ontology_dictionary["representsGroups"]

        for key, value in self.ethics_ontology_dictionary.items():
            ethics_ontology.add((EONS[dataset_name], EONS[key], rdflib.term.Literal(value)))


    def start_processing(self, organisation_name, ethics_ontology):
        self.load_dataset()
        self.questionnaire(organisation_name)
        self.check_vocab()
        self.check_predicate_issues()
        self.fill_ethics_ontology(ethics_ontology)
        print(f"\nDONE PROCESSING DATASET - {self.number_of_datasets}: {self.dataset_name}\n")

        #print(f"Ethics Ontology Dictionary for dataset - {Dataset.number_of_datasets}: {self.dataset_name}\n{self.ethics_ontology_dictionary}\n\n")


def start_execution():
    organisation_name = input("\nPlease input the name of your organisation: ")

    # Importing the ethics ontology
    ethics_ontology = rdflib.Graph()
    ethics_ontology.parse("ontology/EthicsOntology.owl", format = rdflib.util.guess_format('/ontology/EthicsOntology.owl'))

    # Importing the input datasets
    dataset_list = [f for f in os.listdir("Input") if not f.startswith(".")]
    dataset_objects_list = []

    for dataset in dataset_list:
        dataset_object = Dataset(dataset)
        dataset_object.start_processing(organisation_name, ethics_ontology)
        dataset_objects_list.append(dataset_object)

    ethics_ontology.serialize(destination='output/Updated_Ethics_Ontology.owl', format='xml')
    print("\nOutput - Updated Ethics Ontology created")

    # integration_issues()


def main():
    #The following line is to suppress a common warning message by the rdflib package.
    logging.getLogger("rdflib").setLevel(logging.ERROR)

    option = input("\nStarted the tool successfully.\n\nAre all the input datasets in the \"input\" folder? [Y/N]: ")
    if option in yes:
        start_execution()
    elif option in no:
        print("\nOkay! Make sure all the input datasets are in the \"input\" folder and then start the tool.")
        sys.exit()
    else:
        print("Wrong option. Aborting program!")
        sys.exit()

    print("\nTool finished running.\n")


if __name__ == "__main__":
    main()
