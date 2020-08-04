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
    print("\n\nTool finished running. Report has been generated in the \"output\" folder.")
    messagebox.showinfo("Tool finished running","The datasets have been processed and an ethics report has been generated in the \"output\" folder.")

def questionnaire(dataset_name):
    answers_objects = {} # A dictionary containing the objects of every answer field

    lbl_data_controller = tk.Label(window, text=f"Enter the name of the data controller (of {dataset_name}) that the data subject originally agreed to share their data with")
    lbl_data_controller.pack()
    ent_data_controller = tk.Entry()
    ent_data_controller.pack()
    answers_objects["lbl_data_controller"] = lbl_data_controller
    answers_objects["data_controller"] = ent_data_controller

    lbl_files = tk.Label(window, text=f"If any files are attached to the {dataset_name} dataset, then enter some keyword(s) describing the file. Otherwise, leave the entry blank.")
    lbl_files.pack()
    ent_files = tk.Entry()
    ent_files.pack()
    answers_objects["lbl_files"] = lbl_files
    answers_objects["files"] = ent_files

    lbl_data_subject = tk.Label(window, text=f"Are the data subjects of the {dataset_name} dataset individuals or groups?")
    lbl_data_subject.pack()
    rdo_data_subject = tk.StringVar(value="x")
    rdo_individuals = tk.Radiobutton(window, text='Individuals', variable=rdo_data_subject, value="i")
    rdo_groups = tk.Radiobutton(window, text='Groups', variable=rdo_data_subject, value="g")
    rdo_individuals.pack()
    rdo_groups.pack()
    answers_objects["lbl_data_subject"] = lbl_data_subject
    answers_objects["rdo_individuals"] = rdo_individuals
    answers_objects["rdo_groups"] = rdo_groups
    answers_objects["data_subject_type"] = rdo_data_subject

    return answers_objects

def select_file():
    # Reading the text entry widget for the organisation's name.
    global organisation_name
    organisation_name = str(org_name.get())

    # Making sure the entry is not empty or has just spaces.
    if not organisation_name.strip():
        messagebox.showerror("Invalid organisation name", "Please enter a valid organisation name!")
        return

    # Covering the corner case where the select dataset button is clicked again.
    # Have to clear previous widgets
    if dataset_answer_entry_objects:
        for dataset, answers_objects in dataset_answer_entry_objects.items():
            for key, answer_object in answers_objects.items():
                if key != "data_subject_type":
                    answer_object.destroy()
        btn_done.pack_forget()

    window.filenames = filedialog.askopenfilenames(initialdir="/", title="Select Input Datasets", filetypes=(("XML Files", "*.xml"), ("RDF Files", "*.rdf"), ("OWL Files", "*.owl")))

    if lbl_files_chosen["text"].strip():
        filenames = lbl_files_chosen["text"]
    else:
        filenames = ""

    for file in window.filenames:
        input_datasets_locations.append(file)
        file = file.split('/')[-1]
        input_datasets_list.append(file)
        if filenames != "":
            filenames = filenames + ", "+ file
        else:
            filenames = file

    lbl_files_chosen["text"] = filenames

    for dataset in input_datasets_list:
        dataset_answer_entry_objects[dataset] = questionnaire(dataset)

    if input_datasets_list:
        btn_done.pack()

def done():

    for dataset in dataset_answer_entry_objects.keys():
        if not str(dataset_answer_entry_objects[dataset]["data_controller"].get()).strip():
            messagebox.showerror("Invalid data controller", f"No data controller name entered for the dataset - {dataset}. If unknown, enter \"UNKNOWN\" in the entry field.")
            return

        if dataset_answer_entry_objects[dataset]["data_subject_type"].get() == "x":
            messagebox.showerror("No data subject type chosen", f"No selection was made for the data subject type (individual or group) for the dataset - {dataset}")
            return

    for dataset, answers_objects in dataset_answer_entry_objects.items():
        questionnaire_answers_dict[dataset] = {}
        for key, answer_object in answers_objects.items():
            if not key.startswith("lbl") and not key.startswith("rdo"):
                questionnaire_answers_dict[dataset][key] = str(answer_object.get())

    print(f"Answers dictionary: {questionnaire_answers_dict}")
    start_execution()


questionnaire_answers_dict = {} # Dictionary that contains all the answers to the questionnaire about every dataset.
input_datasets_locations = [] # List containing input dataset's file locations.
input_datasets_list = [] #  List containing input datasets' names.
dataset_answer_entry_objects = {} # Dictionary to hold the objects of entry fields in the GUI.
organisation_name = "" # A global variable to store the name of the organisation running this tool.

# Initialising GUI
window = tk.Tk()
window.title("Ethics tool")

# The following line is to suppress a common warning message by the rdflib package.
logging.getLogger("rdflib").setLevel(logging.ERROR)

ethics_ontology = rdflib.Graph()
ethics_ontology.parse("../ontology/EthicsOntology.owl", format = rdflib.util.guess_format('/ontology/EthicsOntology.owl'))

tk.Label(window, text="Please input the name of your organisation: ").pack()
org_name = tk.StringVar() # Stores the current organisation's name.
ent_org_name = tk.Entry(master=window, textvariable=org_name).pack()
lbl_files_chosen = tk.Label(master=window, text=" ")
btn_done = tk.Button(master=window, text="Done", command=done)
lbl_file_chosen_label = tk.Label(master=window, text="Chosen input datasets: ").pack()
lbl_files_chosen.pack()
btn_input = tk.Button(master=window, text="Select Input Datasets", command=select_file)
btn_input.pack()

window.mainloop()
print("\nTool finished running.\n")
