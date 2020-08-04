import os
import rdflib
import logging
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from dataset_manager import InputDataset, OutputDataset

def start_execution():
    for dataset in input_datasets_list:
        dataset_name_without_ext = os.path.splitext(dataset)[0]
        dataset_object = InputDataset(dataset_name_without_ext)
        dataset_file_location = input_datasets_locations[input_datasets_list.index(dataset)]
        dataset_object.start_processing(organisation_name, ethics_ontology, dataset_file_location, questionnaire_answers_dict[dataset])

    output_ontology_name = "Updated_Ethics_Ontology.owl"
    output_ontology_location = f"../output/{output_ontology_name}"
    ethics_ontology.serialize(destination=output_ontology_location, format='xml')
    print("\nOutput - Updated Ethics Ontology created")

    output_ontology_object = OutputDataset(output_ontology_name)
    output_ontology_object.start_processing(output_ontology_location)


def questionnaire(dataset_name):
    answers_objects = {} # A dictionary containing the objects of every answer field

    tk.Label(window, text=f"Enter the name of the data controller (of {dataset_name}) that the data subject originally agreed to share their data with").pack()
    ent_data_controller = tk.Entry()
    ent_data_controller.pack()
    answers_objects["data_controller"] = ent_data_controller

    tk.Label(window, text=f"If any files are attached to the {dataset_name} dataset, then enter some keyword(s) describing the file. Otherwise, leave the entry blank.").pack()
    ent_files = tk.Entry()
    ent_files.pack()
    answers_objects["files"] = ent_files

    tk.Label(window, text=f"Are the data subjects of the {dataset_name} dataset individuals or groups?").pack()
    rdo_data_subject = tk.StringVar()
    individuals = tk.Radiobutton(window, text='Individuals', variable=rdo_data_subject, value="i").pack()
    groups = tk.Radiobutton(window, text='Groups', variable=rdo_data_subject, value="g").pack()
    answers_objects["data_subject_type"] = rdo_data_subject

    return answers_objects

def select_file():
    window.filenames = filedialog.askopenfilenames(initialdir="/", title="Select Input Datasets", filetypes=(("XML Files", "*.xml"), ("RDF Files", "*.rdf"), ("OWL Files", "*.owl")))
    filenames = ""

    for file in window.filenames:
        input_datasets_locations.append(file)
        file = file.split('/')[-1]
        input_datasets_list.append(file)
        if filenames != "":
            filenames = filenames + ", "+ file
        else:
            filenames = file

    organisation_name = org_name.get()
    print(f"Organisation: {organisation_name}")

    lbl_files_chosen["text"] = filenames

    for dataset in input_datasets_list:
        dataset_answer_entry_objects[dataset] = questionnaire(dataset)

    btn_done.pack()

def done():
    for dataset, answers_objects in dataset_answer_entry_objects.items():
        questionnaire_answers_dict[dataset] = {}
        for key, answer_object in answers_objects.items():
            questionnaire_answers_dict[dataset][key] = str(answer_object.get())

    print(f"Answers dictionary: {questionnaire_answers_dict}")
    start_execution()

# def start_execution():
#     # Importing the ethics ontology
#     ethics_ontology = rdflib.Graph()
#     ethics_ontology.parse("../ontology/EthicsOntology.owl", format = rdflib.util.guess_format('/ontology/EthicsOntology.owl'))

#     tk.Label(window, text="Please input the name of your organisation: ").pack()
#     ent_org_name = tk.Entry(master=window, textvariable=organisation_name).pack()
#     lbl_files_chosen = tk.Label(master=window, text=" ")

#     lbl_file_chosen_label = tk.Label(master=window, text="Chosen input datasets: ").pack()
#     lbl_files_chosen.pack()
#     btn_input = tk.Button(master=window, text="Select Input Datasets", command=select_file)
#     btn_done = tk.Button(master=window, text="Done", command=done)
#     btn_input.pack()
#     #btn_done.pack()

#     print(f"Organisation Name: {ent_org_name}")

    # # Importing the input datasets
    # dataset_list = [f for f in os.listdir("Input") if not f.startswith(".") and f != "catalog-v001.xml"]
    # dataset_objects_list = []

    # for dataset in dataset_list:
    #     dataset_object = InputDataset(dataset)
    #     dataset_object.start_processing(organisation_name, ethics_ontology)
    #     dataset_objects_list.append(dataset_object)

    # output_ontology_name = "Updated_Ethics_Ontology.owl"
    # ethics_ontology.serialize(destination=f"output/{output_ontology_name}", format='xml')
    # print("\nOutput - Updated Ethics Ontology created")

    # output_ontology_object = OutputDataset(output_ontology_name)
    # output_ontology_object.start_processing()

    # window.mainloop()


# def main():
#     #The following line is to suppress a common warning message by the rdflib package.
#     logging.getLogger("rdflib").setLevel(logging.ERROR)
#     start_execution()
#     print("\nTool finished running.\n")


# if __name__ == "__main__":
#     main()

#############

questionnaire_answers_dict = {} # Dictionary that contains all the answers to the questionnaire about every dataset.
input_datasets_locations = [] # List containing input dataset's file locations.
input_datasets_list = [] #  List containing input datasets' names.
dataset_answer_entry_objects = {} # Dictionary to hold the objects of entry fields in the GUI
organisation_name = ""


# Initialising GUI
window = tk.Tk()
window.title("Ethics tool")

logging.getLogger("rdflib").setLevel(logging.ERROR)

ethics_ontology = rdflib.Graph()
ethics_ontology.parse("../ontology/EthicsOntology.owl", format = rdflib.util.guess_format('/ontology/EthicsOntology.owl'))

tk.Label(window, text="Please input the name of your organisation: ").pack()
org_name = tk.StringVar() # Stores the current organisation's name.
ent_org_name = tk.Entry(master=window, textvariable=org_name).pack()
lbl_files_chosen = tk.Label(master=window, text=" ")

lbl_file_chosen_label = tk.Label(master=window, text="Chosen input datasets: ").pack()
lbl_files_chosen.pack()
btn_input = tk.Button(master=window, text="Select Input Datasets", command=select_file)
btn_done = tk.Button(master=window, text="Done", command=done)
btn_input.pack()
#btn_done.pack()

window.mainloop()
print("\nTool finished running.\n")
