import os
import rdflib
import logging
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog
from dataset_manager import InputDataset, OutputDataset

class GUI():
    def __init__(self, window, height, width):
        # Initialising some common variables used across methods
        self.window = window
        self.window_height = height
        self.window_width = width
        self.organisation_name = ""
        self.input_datasets_locations = [] # List containing input dataset's file locations.
        self.input_datasets_list = [] #  List containing input datasets' names.
        self.dataset_answer_entry_objects = {} # Dictionary to hold the objects of entry fields in the GUI.
        self.questionnaire_answers_dict = {} # Dictionary that contains all the answers to the questionnaire about every dataset.
        self.organisation_name = "" # A global variable to store the name of the organisation running this tool.

    def get_organisation_name(self):
        # Asking for the name of the organisation running this tool
        while True:
            self.organisation_name = simpledialog.askstring("Organisation Name", "Please input the name of your organisation", parent=self.frm_main)
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
            dataset_object.start_processing(self.organisation_name, self.ethics_ontology, dataset_file_location, self.questionnaire_answers_dict[dataset], self.lbl_logger)

        output_ontology_name = "Updated_Ethics_Ontology.owl"
        output_ontology_location = f"../output/{output_ontology_name}"
        self.ethics_ontology.serialize(destination=output_ontology_location, format='xml')
        print("\nOutput - Updated Ethics Ontology created")

        output_ontology_object = OutputDataset(output_ontology_name)
        output_ontology_object.start_processing(output_ontology_location, self.lbl_logger)
        print("\n\nTool finished running. Report has been generated in the \"output\" folder.")
        messagebox.showinfo("Tool finished running","The datasets have been processed and an ethics report has been generated in the \"output\" folder.")

    def questionnaire(self, dataset_name):
        answers_objects = {} # A dictionary containing the objects of every answer field

        frm_questionnaire = tk.Frame(master=self.frm_all_questionnaire_area, highlightbackground="black", highlightthickness=1)
        frm_questionnaire.pack(fill="both", expand=True)
        answers_objects["frm_questionnaire"] = frm_questionnaire

        lbl_dataset_questionnaire = tk.Label(master=frm_questionnaire, text=f"Questionnaire - {dataset_name}", font="Helvetica 15 bold", borderwidth=1, relief="solid", padx=10, pady=10)
        lbl_dataset_questionnaire.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        answers_objects["lbl_dataset_questionnaire"] = lbl_dataset_questionnaire

        lbl_data_controller = tk.Label(master=frm_questionnaire, text=f"Enter the name of the data controller (of {dataset_name}) that the data subject originally agreed to share their data with")
        ent_data_controller = tk.Entry(master=frm_questionnaire, width = 40)
        lbl_data_controller.grid(row=1, column=0, columnspan=3, padx=10, pady=0, sticky="w")
        ent_data_controller.grid(row=2, column=0, padx=10, pady=(0,10), sticky="nw")
        answers_objects["lbl_data_controller"] = lbl_data_controller
        answers_objects["data_controller"] = ent_data_controller

        lbl_files = tk.Label(master=frm_questionnaire, text=f"If any files are attached to the {dataset_name} dataset, then enter some keyword(s) describing the file. Otherwise, leave the entry blank.")
        ent_files = tk.Entry(master=frm_questionnaire, width = 40)
        lbl_files.grid(row=3, column=0, columnspan=3, padx=10, sticky="w")
        ent_files.grid(row=4, column=0, padx=10, pady=(0,10), sticky="nw")
        answers_objects["lbl_files"] = lbl_files
        answers_objects["files"] = ent_files

        lbl_data_subject = tk.Label(master=frm_questionnaire, text=f"Are the data subjects of the {dataset_name} dataset individuals or groups?")
        rdo_data_subject = tk.StringVar(value="x")
        rdo_individuals = tk.Radiobutton(master=frm_questionnaire, text='Individuals', variable=rdo_data_subject, value="i")
        rdo_groups = tk.Radiobutton(master=frm_questionnaire, text='Groups', variable=rdo_data_subject, value="g")
        lbl_data_subject.grid(row=5, column=0, padx=10, pady=(0,15), sticky="w")
        rdo_individuals.grid(row=5, column=1, padx=10, pady=(0,15), sticky="w")
        rdo_groups.grid(row=5, column=2, padx=10, pady=(0,15), sticky="w")
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
            self.btn_done.grid_forget()

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
            self.btn_done.grid()

    def done(self, event=None):
        for dataset in self.dataset_answer_entry_objects.keys():
            if not str(self.dataset_answer_entry_objects[dataset]["data_controller"].get()).strip():
                messagebox.showerror("Invalid data controller", f"No data controller name entered for the dataset - {dataset}. If unknown, enter \"UNKNOWN\" in the entry field.")
                return

            if self.dataset_answer_entry_objects[dataset]["data_subject_type"].get() == "x":
                messagebox.showerror("No data subject type chosen", f"No selection was made for the data subject type (individual or group) for the dataset - {dataset}")
                return

        widgets_to_avoid = ("lbl", "rdo", "frm")

        for dataset, answers_objects in self.dataset_answer_entry_objects.items():
            self.questionnaire_answers_dict[dataset] = {}
            for key, answer_object in answers_objects.items():
                if not key.startswith(widgets_to_avoid):
                    self.questionnaire_answers_dict[dataset][key] = str(answer_object.get())

        self.lbl_logger.grid()
        self.start_tool_execution()

    def start(self):
        # Initialising frames to be used inside the window
        self.frm_main = tk.Frame(master=self.window)
        self.frm_input_area = tk.Frame(master=self.frm_main, highlightbackground="black", highlightthickness=1)
        self.frm_all_questionnaire_area = tk.Frame(master=self.frm_main)

        # Initialising GUI widgets
        self.btn_input = tk.Button(master=self.frm_input_area, text="Select input datasets", width=30, height=2, command=self.select_file)
        self.lbl_file_chosen_label = tk.Label(master=self.frm_input_area, text="Chosen input datasets: ")
        self.lbl_files_chosen = tk.Label(master=self.frm_input_area, text=" ")
        self.btn_done = tk.Button(master=self.frm_main, text="Done", width = 10, height=2, command=self.done)
        self.btn_done.bind('<Return>', self.done)
        self.lbl_logger = tk.Label(master=self.frm_main, text = "", font="Helvetica 12 bold", padx=10, pady=10)

        # Arranging the frames
        self.frm_main.pack()
        self.frm_input_area.grid(row=0, column=0, padx=10, pady=10)
        self.frm_all_questionnaire_area.grid(row=1, column=0, padx=10, pady=10)

        # Packing the widgets
        self.btn_input.grid(row=0, column=0, padx=10, pady=10)
        self.lbl_file_chosen_label.grid(row=0, column=1, padx=10, pady=10)
        self.lbl_files_chosen.grid(row=0, column=2, padx=10, pady=10)

        # Importing the Ethics Ontology
        self.ethics_ontology = rdflib.Graph()
        self.ethics_ontology.parse("../ontology/EthicsOntology.owl", format = rdflib.util.guess_format('../ontology/EthicsOntology.owl'))

        self.get_organisation_name()


def start_gui():
    # Initialising GUI
    window = tk.Tk()
    window.title("Ethics tool")
    # width  = int(window.winfo_screenwidth() * 0.75)
    # height = int(window.winfo_screenheight() * 0.75)
    width = 1000
    height = 750
    window.geometry(f"{width}x{height}")
    gui = GUI(window, height, width)
    gui.start()
    window.mainloop()

if __name__ == "__main__":
    # The following line is to suppress a common warning message by the rdflib package.
    logging.getLogger("rdflib").setLevel(logging.ERROR)
    start_gui()
    print("\nTool finished running.\n")
