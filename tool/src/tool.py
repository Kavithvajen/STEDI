import os
import rdflib
import logging
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog
from dataset_manager import InputDataset, OutputDataset

class GUI():
    def __init__(self, window):
        self.window = window
        self.organisation_name = ""
        self.input_datasets_locations = [] # List containing input dataset's file locations.
        self.input_datasets_list = [] #  List containing input datasets' names.
        self.dataset_answer_entry_objects = {} # Dictionary to hold the objects of entry fields in the GUI.
        self.questionnaire_answers_dict = {} # Dictionary that contains all the answers to the questionnaire about every dataset.
        self.organisation_name = "" # A global variable to store the name of the organisation running this tool.
        self.ethics_ontology = rdflib.Graph()
        self.ethics_ontology.parse("../ontology/EthicsOntology.owl", format = rdflib.util.guess_format('../ontology/EthicsOntology.owl'))

    def get_organisation_name(self):
        # Asking for the name of the organisation running this tool
        while True:
            self.organisation_name = simpledialog.askstring("Organisation Name", "Please input the name of your organisation", parent=self.window)
            if (self.organisation_name is None) or (not self.organisation_name.strip()):
                messagebox.showerror("Invalid organisation name", "Please enter a valid organisation name!")
                continue
            else:
                break

    def start_tool_execution(self):
        for dataset in self.input_datasets_list:
            dataset_name_without_ext = os.path.splitext(dataset)[0]
            dataset_object = InputDataset(dataset_name_without_ext)
            dataset_file_location = self.input_datasets_locations[self.input_datasets_list.index(dataset)]
            dataset_object.start_processing(self.organisation_name, self.ethics_ontology, dataset_file_location, self.questionnaire_answers_dict[dataset])

        output_ontology_name = "Updated_Ethics_Ontology.owl"
        output_ontology_location = f"../output/{output_ontology_name}"
        self.ethics_ontology.serialize(destination=output_ontology_location, format='xml')
        print("\nOutput - Updated Ethics Ontology created")

        output_ontology_object = OutputDataset(output_ontology_name)
        output_ontology_object.start_processing(output_ontology_location)
        print("\n\nTool finished running. Report has been generated in the \"output\" folder.")
        messagebox.showinfo("Tool finished running","The datasets have been processed and an ethics report has been generated in the \"output\" folder.")

    def questionnaire(self, dataset_name):
        answers_objects = {} # A dictionary containing the objects of every answer field

        lbl_data_controller = tk.Label(self.window, text=f"Enter the name of the data controller (of {dataset_name}) that the data subject originally agreed to share their data with")
        lbl_data_controller.pack()
        ent_data_controller = tk.Entry()
        ent_data_controller.pack()
        answers_objects["lbl_data_controller"] = lbl_data_controller
        answers_objects["data_controller"] = ent_data_controller

        lbl_files = tk.Label(self.window, text=f"If any files are attached to the {dataset_name} dataset, then enter some keyword(s) describing the file. Otherwise, leave the entry blank.")
        lbl_files.pack()
        ent_files = tk.Entry()
        ent_files.pack()
        answers_objects["lbl_files"] = lbl_files
        answers_objects["files"] = ent_files

        lbl_data_subject = tk.Label(self.window, text=f"Are the data subjects of the {dataset_name} dataset individuals or groups?")
        lbl_data_subject.pack()
        rdo_data_subject = tk.StringVar(value="x")
        rdo_individuals = tk.Radiobutton(self.window, text='Individuals', variable=rdo_data_subject, value="i")
        rdo_groups = tk.Radiobutton(self.window, text='Groups', variable=rdo_data_subject, value="g")
        rdo_individuals.pack()
        rdo_groups.pack()
        answers_objects["lbl_data_subject"] = lbl_data_subject
        answers_objects["rdo_individuals"] = rdo_individuals
        answers_objects["rdo_groups"] = rdo_groups
        answers_objects["data_subject_type"] = rdo_data_subject

        return answers_objects

    def select_file(self):
        # Covering the corner case where the select dataset button is clicked again.
        # Have to clear previous widgets.
        if self.dataset_answer_entry_objects:
            for dataset, answers_objects in self.dataset_answer_entry_objects.items():
                for key, answer_object in answers_objects.items():
                    if key != "data_subject_type":
                        answer_object.destroy()
            self.btn_done.pack_forget()

        self.window.filenames = filedialog.askopenfilenames(initialdir="/", title="Select Input Datasets", filetypes=(("XML Files", "*.xml"), ("RDF Files", "*.rdf"), ("OWL Files", "*.owl")))

        if self.lbl_files_chosen["text"].strip():
            filenames = self.lbl_files_chosen["text"]
        else:
            filenames = ""

        for file in self.window.filenames:
            self.input_datasets_locations.append(file)
            file = file.split('/')[-1]
            self.input_datasets_list.append(file)
            if filenames != "":
                filenames = filenames + ", "+ file
            else:
                filenames = file

        self.lbl_files_chosen["text"] = filenames

        for dataset in self.input_datasets_list:
            self.dataset_answer_entry_objects[dataset] = self.questionnaire(dataset)

        if self.input_datasets_list:
            self.btn_done.pack()

    def done(self):
        for dataset in self.dataset_answer_entry_objects.keys():
            if not str(self.dataset_answer_entry_objects[dataset]["data_controller"].get()).strip():
                messagebox.showerror("Invalid data controller", f"No data controller name entered for the dataset - {dataset}. If unknown, enter \"UNKNOWN\" in the entry field.")
                return

            if self.dataset_answer_entry_objects[dataset]["data_subject_type"].get() == "x":
                messagebox.showerror("No data subject type chosen", f"No selection was made for the data subject type (individual or group) for the dataset - {dataset}")
                return

        for dataset, answers_objects in self.dataset_answer_entry_objects.items():
            self.questionnaire_answers_dict[dataset] = {}
            for key, answer_object in answers_objects.items():
                if not key.startswith("lbl") and not key.startswith("rdo"):
                    self.questionnaire_answers_dict[dataset][key] = str(answer_object.get())

        print(f"Answers dictionary: {self.questionnaire_answers_dict}")
        self.start_tool_execution()

    def start(self):
        self.lbl_files_chosen = tk.Label(master=self.window, text=" ")
        self.btn_done = tk.Button(master=self.window, text="Done", command=self.done)
        self.lbl_file_chosen_label = tk.Label(master=self.window, text="Chosen input datasets: ")
        self.lbl_file_chosen_label.pack()
        self.lbl_files_chosen.pack()
        self.btn_input = tk.Button(master=self.window, text="Select Input Datasets", command=self.select_file)
        self.btn_input.pack()

        self.get_organisation_name()


if __name__ == "__main__":
    # The following line is to suppress a common warning message by the rdflib package.
    logging.getLogger("rdflib").setLevel(logging.ERROR)

    # Initialising GUI
    window = tk.Tk()
    window.title("Ethics tool")
    gui = GUI(window)
    gui.start()
    window.mainloop()

    print("\nTool finished running.\n")
