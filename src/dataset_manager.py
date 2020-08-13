import copy
import json
import re
import os
import ast
import spacy
import requests
import rdflib
from rdflib.namespace import RDF, RDFS, OWL, XSD

# Globally loading the language model to avoid loading it everytime it's used
nlp = spacy.load("en_core_web_md")

# Ethics Ontology Namespace
EONS = rdflib.Namespace("https://www.scss.tcd.ie/~kamarajk/EthicsOntology#")

class _Dataset():
    # To be able to effectively ignore these common predictes and tokens while processing the dataset.
    common_schema_predicates = (RDF.type, RDFS.range, RDFS.domain, RDFS.label, OWL.imports)
    common_words_to_ignore = ["as", "the", "is", "of", "has"]

    def __init__(self, dataset_name):
        self.dataset_name = dataset_name
        self.graph = rdflib.Graph()
        self.ethics_ontology_dictionary = {
            "hasAge": {"value": False, "trigger_items": {"VOCABULARIES": [], "PREDICATES": []}},
            "hasBehaviourData": {"value": False, "trigger_items": {"VOCABULARIES": [], "PREDICATES": []}},
            "hasChildData": {"value": False, "trigger_items": {"VOCABULARIES": [], "PREDICATES": []}},
            "hasContactInformation": {"value": False, "trigger_items": {"VOCABULARIES": [], "PREDICATES": []}},
            "hasCriminalActivity": {"value": False, "trigger_items": {"VOCABULARIES": [], "PREDICATES": []}},
            "hasDataControllerName": {"value": False},
            "hasEthnicityData": {"value": False, "trigger_items": {"VOCABULARIES": [], "PREDICATES": []}},
            "hasFilesWithPIIAttached": {"value": False},
            "hasHealthData": {"value": False, "trigger_items": {"VOCABULARIES": [], "PREDICATES": []}},
            "hasIncomeData": {"value": False, "trigger_items": {"VOCABULARIES": [], "PREDICATES": []}},
            "hasLoanRecords": {"value": False, "trigger_items": {"VOCABULARIES": [], "PREDICATES": []}},
            "hasLocationData": {"value": False, "trigger_items": {"VOCABULARIES": [], "PREDICATES": []}},
            "hasName": {"value": False, "trigger_items": {"VOCABULARIES": [], "PREDICATES": []}},
            "hasPhysicalCharacteristics": {"value": False, "trigger_items": {"VOCABULARIES": [], "PREDICATES": []}},
            "hasPoliticalOpinions": {"value": False, "trigger_items": {"VOCABULARIES": [], "PREDICATES": []}},
            "hasReligion": {"value": False, "trigger_items": {"VOCABULARIES": [], "PREDICATES": []}},
            "hasSignedNDA": {"value": False, "trigger_items": {"VOCABULARIES": [], "PREDICATES": []}},
            "hasTooManyDataPoints": {"value": False},
            "hasUserTrackingData": {"value": False, "trigger_items": {"VOCABULARIES": [], "PREDICATES": []}},
            "isValidForProcessing": {"value": False},
            "representsGroups": {"value": False},
            "representsIndividuals": {"value": False}
        }

    def list_individuals(self):
        individuals = [subject for subject in self.graph.subjects(predicate=RDF.type, object=OWL.NamedIndividual)]
        return individuals

    def load_dataset(self, file_location):
        self.graph.parse(file_location, format=rdflib.util.guess_format(file_location))
        self.graph.serialize(format="xml")


class InputDataset(_Dataset):
    number_of_datasets = 0

    def __init__(self, dataset_name):
        super().__init__(dataset_name)
        InputDataset.number_of_datasets += 1

    def questionnaire(self, organisation_name, questionnaire_answers):
        # To check if the data subject has provided the data controller consent to process their data.
        self.ethics_ontology_dictionary["hasDataControllerName"]["value"] = questionnaire_answers["data_controller"]
        if organisation_name.lower() == questionnaire_answers["data_controller"].lower():
            self.ethics_ontology_dictionary["isValidForProcessing"]["value"] = True

        # To check if any PII is present in attached files.
        if questionnaire_answers["files"] != "":
            file_name = questionnaire_answers["files"].lower()
            file_name = re.sub("[^a-z ]+", " ", file_name)

            issue_tokens = ("resume", "cv","photo", "scan", "finance", "doctor", "personal", "certificate", "proof", "record")

            file_name_tokens = nlp(file_name)

            for token in file_name_tokens:
                for issue in issue_tokens:
                    # To avoid checking similarity for empty vectors.
                    if token.has_vector and token.similarity(nlp(issue)) > 0.5:
                        self.ethics_ontology_dictionary["hasFilesWithPIIAttached"]["value"] = True

        # To identify the data subject type.
        if questionnaire_answers["data_subject_type"] == "i":
            self.ethics_ontology_dictionary["representsIndividuals"]["value"] = True
        else:
            self.ethics_ontology_dictionary["representsGroups"]["value"] = True

    def check_vocab(self):
        # Method to check for potentially risky vocabularies
        URL = "https://lov.linkeddata.es/dataset/lov/api/v2/vocabulary/info?"
        network_error = False

        for vocab in self.graph.namespace_manager.namespaces():
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
                            self.ethics_ontology_dictionary[namespace[1]]["value"] = True
                            self.ethics_ontology_dictionary[namespace[1]]["trigger_items"]["VOCABULARIES"].append(vocab[0])

    def predicate_processor(self, word_lists_dict):
        for p in self.graph.predicates():
            if p not in _Dataset.common_schema_predicates:
                predicate_parts = p.split("/")
                predicate = predicate_parts[-1]
                predicate = re.sub("[^A-Za-z0-9 ]+", " ", predicate)
                # To split camel case
                predicate = re.sub(r"([A-Z])", r" \1", predicate)
                predicate = predicate.lower()

                predicate_tokens = nlp(predicate)

                for token in predicate_tokens:
                    if token.text not in _Dataset.common_words_to_ignore:
                        for word_list in word_lists_dict.values():
                            for issue in word_list[0]:
                                # 1st condition checks if its the same thing, this eliminates the unnecessary use of NLP.
                                # 2nd condition avoids checking similarity for empty vectors first and then does the similarity check.
                                # "0.5" allowed a wider range of words to creep in as issues, so after trial and error I settled on "0.6".
                                if (str(token).lower() == issue.lower()) or (token.has_vector and token.similarity(nlp(issue)) > 0.6) :
                                    data_property = [word_list[1]][0]
                                    self.ethics_ontology_dictionary[data_property]["value"] = True
                                    if str(p) not in self.ethics_ontology_dictionary[data_property]["trigger_items"]["PREDICATES"]:
                                        self.ethics_ontology_dictionary[data_property]["trigger_items"]["PREDICATES"].append(str(p))

    def check_individual_specific_issues(self):
        # Checking if any individual in the dataset has too many data points.
        individuals = self.list_individuals()

        for i in individuals:
            no_of_data_points = 0
            for p in self.graph.predicates(subject=i):
                if p not in _Dataset.common_schema_predicates:
                    no_of_data_points += 1

            # No reason why having 10 data points is high.
            # A number can be fixed if extensive research was conducted in this exact area.
            if no_of_data_points >= 10:
                self.ethics_ontology_dictionary["hasTooManyDataPoints"]["value"] = True
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

    def check_predicate_issues(self):
        # print(f"\n* Checking for potential ethics issues in the predicates of dataset - {self.number_of_datasets}")

        # Seperately checking for the individual specific ethics issues
        if self.ethics_ontology_dictionary["representsIndividuals"]["value"] == True:
            self.check_individual_specific_issues()

        # Using list inside of the tuple to keep the list of words as an iterable objects when unpacking the tuple.
        # If it were a tuple inside a tuple, then when only a single object (name, politics, etc) is present, the word
        # itself will be iterated upon. Thereby loosing meaning and only a bunch of characters will be present.
        word_lists_dict = {
            "age_words" : (["age", "birthday", "dob"],
                            "hasAge"),

            "behaviour_words" : (["behaviour", "behavioural", "myers", "opinion", "personality"],
                            "hasBehaviourData"),

            "child_words" : (["baby", "child", "juvenile", "kid", "minor", "teenager", "youngster"],
                            "hasChildData"),

            "criminal_words" : (["criminal", "felony", "jail", "prison"],
                            "hasCriminalActivity"),

            "ethnic_words" : (["accent", "community", "dialect", "immigrant", "language", "race", "religion"],
                            "hasEthnicityData"),

            "health_words" : (["DNA", "consult", "doctor", "health", "medical"],
                            "hasHealthData"),

            "income_words" : (["earning", "economic", "financial", "income", "salary"],
                            "hasIncomeData"),

            "loan_words" : (["debt", "loan"],
                            "hasLoanRecords"),

            "location_words" : (["address", "area", "city", "lives, ""location", "postal", "resident", "zip-code"],
                            "hasLocationData"),

            "physical_words" : (["body", "colour", "disability", "gender", "hair", "height", "piercings",
                                    "size", "skin", "tattoos", "weight"],
                            "hasPhysicalCharacteristics"),

            "politics_words" : (["politics"],
                            "hasPoliticalOpinions"),

            "religion_words" : (["divinity", "faith", "religion", "worship"],
                            "hasReligion"),

            "tracking_words" : (["advertisement", "browser", "history", "search", "tracking"],
                            "hasUserTrackingData")
        }

        self.predicate_processor(word_lists_dict)

    def fill_ethics_ontology(self, ethics_ontology):
        # print(f"\n* Filling the ethics ontology for dataset - {self.number_of_datasets}")

        # Cleaning up dataset_name so the individuals of the ethics ontology follow a consistent naming convention.
        dataset_name = os.path.splitext(self.dataset_name)[0]
        dataset_name = re.sub("[^A-Za-z0-9 ]+", " ", dataset_name)
        dataset_name = re.sub("[ ]+", " ", dataset_name)
        dataset_name = dataset_name.replace(" ", "_")

        # Creates a named individual with the name of the dataset
        ethics_ontology.add((EONS[dataset_name], RDF.type, OWL.NamedIndividual))

        # Identifying data subject type and removing that data from the dictionary
        if self.ethics_ontology_dictionary["representsIndividuals"]["value"] == True:
            ethics_ontology.add((EONS[dataset_name], RDF.type, EONS.Individual))
            del self.ethics_ontology_dictionary["representsIndividuals"]
            del self.ethics_ontology_dictionary["representsGroups"]

        else:
            ethics_ontology.add((EONS[dataset_name], RDF.type, EONS.Group))
            del self.ethics_ontology_dictionary["representsIndividuals"]
            del self.ethics_ontology_dictionary["representsGroups"]

        for issue, issue_info in self.ethics_ontology_dictionary.items():
            ethics_ontology.add((EONS[dataset_name], EONS[issue], rdflib.term.Literal(issue_info["value"])))

            if "trigger_items" in self.ethics_ontology_dictionary[issue]:
                if self.ethics_ontology_dictionary[issue]["trigger_items"]["VOCABULARIES"] or self.ethics_ontology_dictionary[issue]["trigger_items"]["PREDICATES"]:
                    ethics_ontology.add((EONS[dataset_name], EONS[f"{issue}TriggeredBy"], rdflib.term.Literal(issue_info["trigger_items"])))

    def start_processing(self, organisation_name,
            ethics_ontology, file_location, questionnaire_answers,
            logger, progress_bar, progress_value):
        self.load_dataset(file_location)
        logger["text"] = f"SUCCESSFULLY LOADED {self.dataset_name}"
        logger.update()
        progress_bar["value"] += progress_value

        self.questionnaire(organisation_name, questionnaire_answers)

        logger["text"] = f"CHECKING NAMESPACE OF {self.dataset_name}"
        logger.update()
        self.check_vocab()
        progress_bar["value"] += progress_value

        logger["text"] = f"CHECKING PREDICATES OF {self.dataset_name}"
        logger.update()
        self.check_predicate_issues()
        progress_bar["value"] += progress_value

        logger["text"] = f"FILLING ETHICS ONTOLOGY FOR {self.dataset_name}"
        logger.update()
        self.fill_ethics_ontology(ethics_ontology)
        progress_bar["value"] += progress_value

        logger["text"] = f"DONE PROCESSING - {self.dataset_name}"
        logger.update()
        progress_bar["value"] += progress_value
        # print(f"\nDONE PROCESSING DATASET - {self.number_of_datasets}: {self.dataset_name}\n")


class OutputDataset(_Dataset):
    def __init__(self, dataset_name, report_location):# Name of the ethics ontology itself. i.e., UPDATED_ETHICS_ONTOLOGY.OWL
        super().__init__(dataset_name)

        self.ethics_dicts_dict = {} # A master dictionary to hold all the ethics_dictionary values of every dataset
        dataset_name = os.path.splitext(self.dataset_name)[0]
        self.ethics_report_name = "Ethics_Report.txt"
        self.report_location = report_location

        self.scenario_1_issues = {
            "hasCriminalActivity":  False,
            "hasEthnicityData": False,
            "hasLocationData": False,
            "hasReligion": False
        }

        self.scenario_2_issues = {
            "hasBehaviourData": False,
            "hasLoanRecords": False,
            "hasUserTrackingData": False
        }

        self.scenario_3_issues = {
            "hasUserTrackingData": False,
            "hasName": False,
            "hasBehaviourData": False,
            "hasLocationData": False
        }

        self.scenario_4_issues = {
            "hasAge": False,
            "hasBehaviourData": False,
            "hasEthnicityData": False,
            "hasIncomeData": False,
            "hasLocationData": False,
            "hasPoliticalOpinions": False,
            "hasReligion": False
        }

        # Removing previous reports.
        if os.path.exists(f"{self.report_location}/{self.ethics_report_name}"):
            os.remove(f"{self.report_location}/{self.ethics_report_name}")

    def reset_ethics_ontology_dictionary(self):
        for key in self.ethics_ontology_dictionary.keys():
            self.ethics_ontology_dictionary[key]["value"] = False
            if "trigger_items" in self.ethics_ontology_dictionary[key]:
                self.ethics_ontology_dictionary[key]["trigger_items"] = {"VOCABULARIES": [], "PREDICATES": []}

    def querying_service(self):
        # print("\n* Querying the ethics ontology")
        individuals = self.list_individuals()

        for individual in individuals:
            for predicate in self.ethics_ontology_dictionary.keys():
                if (individual, EONS[predicate], rdflib.term.Literal(True)) in self.graph:
                    self.ethics_ontology_dictionary[predicate]["value"] = True
                    self.ethics_ontology_dictionary[predicate]["trigger_items"] = ast.literal_eval(str(self.graph.value(subject=individual, predicate=EONS[f"{predicate}TriggeredBy"])))

            if (individual, RDF.type, EONS.Individual) in self.graph:
                self.ethics_ontology_dictionary["representsIndividuals"]["value"] = True
            else:
                self.ethics_ontology_dictionary["representsGroups"]["value"] = True

            self.ethics_ontology_dictionary["hasDataControllerName"]["value"] = str(self.graph.value(subject=individual, predicate=EONS.hasDataControllerName))

            # Extracting the name of the dataset from the individual URL
            # (E.g.: www.scss.tcs.ie/~kamarajk#Vocab-Dataset) -> Vocab-Dataset
            individual_parts = individual.split("#")
            dataset = individual_parts[-1]

            self.ethics_dicts_dict[dataset] = copy.deepcopy(self.ethics_ontology_dictionary)
            self.reset_ethics_ontology_dictionary()

    def quick_issue_checker(self, issue, dataset):
        # A method to just check for specific issues to see if they can be a linking point.
        for d, e_dict in self.ethics_dicts_dict.items():
            if d != dataset and e_dict[issue]["value"] == True:
                return True

        return False

    def check_integration_issue_scenarios(self):
        for dataset, ethics_dict in self.ethics_dicts_dict.items():
            # Scenario-1 : Check for ethnicity-criminal associations being made.
            for issue in self.scenario_1_issues.keys():
                if ethics_dict[issue]["value"] == True:
                    if issue == "hasLocationData": # A minimum of 2 datasets need have location data to provide linkage between the datasets.
                        self.scenario_1_issues[issue] = self.quick_issue_checker(issue, dataset)
                    else:
                        self.scenario_1_issues[issue] = True

            # Scenario-2 : Check for behaviour-loan repayment associations being made.
            for issue in self.scenario_2_issues.keys():
                if ethics_dict[issue]["value"] == True:
                    if issue == "hasUserTrackingData": # A minimum of 2 datasets need have tracking data to provide linkage between the datasets.
                        self.scenario_2_issues[issue] = self.quick_issue_checker(issue, dataset)
                    else:
                        self.scenario_2_issues[issue] = True

            # Scenario-3 : Check for social media activity used to manipulate insurance rates.
            for issue in self.scenario_3_issues.keys():
                if ethics_dict[issue]["value"] == True:
                    if issue == "hasBehaviourData":
                        self.scenario_3_issues[issue] = True
                    else: # Tracking, name & location need to be common to provide some linkage between the datasets.
                        self.scenario_3_issues[issue] = self.quick_issue_checker(issue, dataset)

            # Scenario-4 : Check for tailored reality/ filtered bubble issue caused by grouping of political opinions and other factors.
            for issue in self.scenario_4_issues.keys():
                if ethics_dict[issue]["value"] == True:
                    if issue == "hasPoliticalOpinions":
                        self.scenario_4_issues[issue] = True
                    else: # Age, behaviour, ethnicity, income, location, religion need to be common to provide some linkage between the datasets.
                        self.scenario_4_issues[issue] = self.quick_issue_checker(issue, dataset)

    def report_writer(self, scenario, text):
        with open(f"{self.report_location}/{self.ethics_report_name}", "a") as writer:
            writer.write(f"\n + {scenario.upper()} : {text}\n")

    def report_generation_service(self):
        predicates_to_ignore = ("hasDataControllerName", "hasFilesWithPIIAttached", "hasTooManyDataPoints", "isValidForProcessing", "representsGroups", "representsIndividuals")
        with open(f"{self.report_location}/{self.ethics_report_name}", "a") as writer:
            for dataset, e_dict in self.ethics_dicts_dict.items():
                writer.write(f"\n\nETHICS REPORT FOR INDIVIDUAL DATASET - {dataset.upper()}\n")
                writer.write(f"\nData controller: {e_dict['hasDataControllerName']['value']}")
                writer.write(f"\nValid for processing: {e_dict['isValidForProcessing']['value']}")
                if e_dict["representsGroups"]["value"] == True:
                    writer.write("\nThis dataset represents groups.")
                else:
                    writer.write("\nThis dataset represents individuals.")
                writer.write("\n\nIssues present in the dataset:\n")

                if e_dict["hasTooManyDataPoints"]["value"] == True:
                    writer.write("\nHAS TOO MANY DATA POINTS\n")

                if e_dict["hasFilesWithPIIAttached"]["value"] == True:
                    writer.write("\nHAS FILES WITH PII ATTACHED\n")

                for key, issue_info in e_dict.items():
                    if key not in predicates_to_ignore and issue_info["value"] == True:
                        split_key = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)',key)
                        split_key_list = [i.group(0) for i in split_key]

                        for word in split_key_list:
                            if split_key_list.index(word) == 0:
                                split_key_list[split_key_list.index(word)] = word.capitalize()

                            elif word != "NDA" and word!= "PII":
                                split_key_list[split_key_list.index(word)] = word.lower()

                            else:
                                pass

                        issue = " ".join([str(element) for element in split_key_list])

                        writer.write(f"\n{issue.upper()}")

                        if "trigger_items" in issue_info and issue_info["trigger_items"] != None:
                            if issue_info["trigger_items"]["VOCABULARIES"]:
                                writer.write("\nVocabularies that triggered the issue: ")
                                for i, vocab_issue in enumerate(issue_info["trigger_items"]["VOCABULARIES"]):
                                    if i:
                                        writer.write(", ")
                                    writer.write(vocab_issue)

                            if issue_info["trigger_items"]["PREDICATES"]:
                                writer.write("\nPredicates that triggered the issue: ")
                                for i, pred_issue in enumerate(issue_info["trigger_items"]["PREDICATES"]):
                                    if i:
                                        writer.write(", ")
                                    writer.write(pred_issue)

                        writer.write("\n\n")

                writer.write("-"*100)
                writer.write("\n")

            writer.write("-"*100)
            writer.write(f"\n\nETHICS REPORT FOR DATA INTEGRATION OF ALL DATASETS\n\n")

        # Scenario-1 report
        scenario = "Scenario-1"
        if self.scenario_1_issues["hasLocationData"] == True and self.scenario_1_issues["hasCriminalActivity"] == True:
            if self.scenario_1_issues["hasReligion"] == True:
                self.report_writer(scenario, "Locations can be linked and certain races can be unethically claimed as more inclined to be criminals.")
            if self.scenario_1_issues["hasEthnicityData"] == True:
                self.report_writer(scenario, "Location can be linked and certain ethnic groups can be unethically claimed as more inclined to be criminals.")
            self.report_writer(scenario, "Since locations can be linked and criminal data is involved, any datapoint from any of the datasets can be used to make ethically wrong assumptions. ")

        # Scenario-2 report
        scenario = "Scenario-2"
        if self.scenario_2_issues["hasUserTrackingData"] == True and self.scenario_2_issues["hasLoanRecords"] == True:
            if self.scenario_2_issues["hasBehaviourData"] == True:
                self.report_writer(scenario, "By cross-site tracking a user, unethical assumptions can be made with regards to their loan repayment capabilities and their general interest/behaviour.")
            self.report_writer(scenario, "Cross-site tracking can be linked with the user's loan records to make any unethical assumption regarding the user.")

        # Scenario-3 report
        scenario = "Scenario-3"
        if self.scenario_3_issues["hasBehaviourData"] == True:
            if self.scenario_3_issues["hasUserTrackingData"] == True:
                self.report_writer(scenario, "Based on cross-site tracking data and the behavioural data of a user, unethical assumptions can be made about the user's activities thereby manipulating insurance rates.")
                self.report_writer(scenario, "Unethical assumption can also be made about the activities of the user's connections (friends, family, followers) on social media accounts.")
                self.report_writer(scenario, "Online tracking details of a user is very sensitive. It can be combined with any other data about the individual to gain extra information that the user did not consent to originally.")
            if self.scenario_3_issues["hasName"] == True:
                self.report_writer(scenario, "A user's name & behaviour can be combined to accordingly hike insurance rates. Combined with other data like cross-site tracking, a lot of unethical assumptions can be made about the user and the people in their life.")
            if self.scenario_3_issues["hasLocationData"] == True:
                self.report_writer(scenario, "Residents of certain localities might have to pay higher insurance rates due to unethical assumptions that link behaviour and location of people.")

        # Scenario-4 report
        scenario = "Scenario-4"
        if self.scenario_4_issues["hasPoliticalOpinions"] == True:
            if self.scenario_4_issues["hasAge"] == True:
                self.report_writer(scenario, "Certain users can be unethically targeted with others' political opinions just because they belong to the same age group.")
            if self.scenario_4_issues["hasBehaviourData"] == True:
                self.report_writer(scenario, "Certain users can be unethically targeted with others' political opinions just because they exhibit similar behaviour.")
            if self.scenario_4_issues["hasEthnicityData"] == True:
                self.report_writer(scenario, "Certain users can be unethically targeted with others' political opinions just because they belong to the same ethnic group.")
            if self.scenario_4_issues["hasIncomeData"] == True:
                self.report_writer(scenario, "Certain users can be unethically targeted with others' political opinions just because they belong to the same income bracket.")
            if self.scenario_4_issues["hasLocationData"] == True:
                self.report_writer(scenario, "Certain users can be unethically targeted with others' political opinions just because they reside in the same area.")
            if self.scenario_4_issues["hasReligion"] == True:
                self.report_writer(scenario, "Certain users can be unethically targeted with others' political opinions just because they believe in the same religion.")

    def start_processing(self, file_location, logger, progress_bar, progress_value):
        self.load_dataset(file_location)
        logger["text"] = f"LOADED OUTPUT DATASET - {self.dataset_name}"
        logger.update()
        progress_bar["value"] += progress_value

        logger["text"] = "QUERYING THE ONTOLOGY"
        logger.update()
        self.querying_service()
        progress_bar["value"] += progress_value

        logger["text"] = "CHECKING FOR INTEGRATION ISSUE SCENARIOS"
        logger.update()
        self.check_integration_issue_scenarios()
        progress_bar["value"] += progress_value

        logger["text"] = "GENERATING REPORT"
        logger.update()
        self.report_generation_service()
        progress_bar["value"] += progress_value

        logger["text"] = "DONE"
