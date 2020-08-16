import os
import rdflib
import logging
import platform
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import ttk, HORIZONTAL, VERTICAL
from dataset_manager import InputDataset, OutputDataset

class GUI():
    def __init__(self, window, OS):
        # Initialising some common variables used across methods
        self.window = window
        self.os = OS
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
        progress_value = 100 / ((len(self.input_datasets_list) *  5) + 5)
        for dataset in self.input_datasets_list:
            dataset_name_without_ext = os.path.splitext(dataset)[0]
            dataset_object = InputDataset(dataset_name_without_ext)
            dataset_file_location = self.input_datasets_locations[self.input_datasets_list.index(dataset)]
            dataset_object.start_processing(self.organisation_name, self.ethics_ontology, dataset_file_location,
                self.questionnaire_answers_dict[dataset], self.lbl_logger, self.progress_bar, progress_value)

        output_ontology_name = "Updated_Ethics_Ontology.owl"
        output_ontology_location = f"../output/{output_ontology_name}"
        self.ethics_ontology.serialize(destination=output_ontology_location, format='xml')
        self.progress_bar["value"] += progress_value

        report_location = ""

        while not report_location:
            messagebox.showinfo("Choose report location", "The datasets have been processed. Choose a location to save the ethics report.")
            report_location = filedialog.askdirectory(title="Choose location to save report")

        output_ontology_object = OutputDataset(output_ontology_name, report_location)
        output_ontology_object.start_processing(output_ontology_location, self.lbl_logger, self.progress_bar, progress_value)
        messagebox.showinfo("Tool finished running","The ethics report has been generated in the chosen location.")


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

        self.window.filenames = filedialog.askopenfilenames(initialdir="/", title="Select Input Datasets", filetypes=(("XML Files", "*.xml"), ("RDF Files", "*.rdf"), ("OWL Files", "*.owl"), ("TTL Files", "*.ttl")))

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
        # In case the done button is pressed again, the progressbar and the logger must be cleared
        self.lbl_logger["text"] = ""
        self.progress_bar["value"] = 0

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

        self.progress_bar.grid(pady=(20,5))
        self.lbl_logger.grid()
        self.start_tool_execution()

    def _on_mousewheel(self, event):
        # Internal method to use mouse scroll for scrolling the window
        if self.os == "Darwin":
            self.main_canvas.yview_scroll(-1*(event.delta), "units")
        else:
            self.main_canvas.yview_scroll(-1*(event.delta/120), "units")

    def start(self):
        # Initialising & configuring frames and canvases for the window to be scrollable
        self.frm_outer = tk.Frame(self.window)
        self.frm_outer.pack(fill=tk.BOTH, expand=1)

        self.main_canvas = tk.Canvas(self.frm_outer)
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.scroll_bar = ttk.Scrollbar(self.frm_outer, orient=VERTICAL, command=self.main_canvas.yview)
        self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        self.main_canvas.configure(yscrollcommand=self.scroll_bar.set)
        self.main_canvas.bind("<Configure>", lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))

        self.frm_main = tk.Frame(master=self.main_canvas)

        self.main_canvas.create_window((0,0), window=self.frm_main, anchor="nw")

        # Based on system OS, setting mouse scroll event to scroll the window
        if self.os == "Linux":
            self.main_canvas.bind_all("<4>", self._on_mousewheel)
            self.main_canvas.bind_all("<5>", self._on_mousewheel)
        else:
            self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Initialising frames to be used inside the window by other widgets
        self.frm_input_area = tk.Frame(master=self.frm_main, highlightbackground="black", highlightthickness=1)
        self.frm_all_questionnaire_area = tk.Frame(master=self.frm_main)

        # Initialising GUI widgets
        self.btn_input = tk.Button(master=self.frm_input_area, text="Select input datasets", width=30, height=2, command=self.select_file)
        self.lbl_file_chosen_label = tk.Label(master=self.frm_input_area, text="Chosen input datasets: ")
        self.lbl_files_chosen = tk.Label(master=self.frm_input_area, text=" ")
        self.btn_done = tk.Button(master=self.frm_main, text="Done", width = 10, height=2, command=self.done)
        self.btn_done.bind('<Return>', self.done)
        self.progress_bar = ttk.Progressbar(master=self.frm_main, orient=HORIZONTAL, length=300, mode='determinate')
        self.lbl_logger = tk.Label(master=self.frm_main, text = "", font="Helvetica 12 bold", padx=10, pady=10)

        # Arranging the frames
        # self.frm_main.pack()
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
    OS = platform.system()
    # Initialising GUI
    window = tk.Tk()
    window.title("STEDI (Support Tool for Ethical Data Integration)")
    width = 1000
    height = 750
    window.geometry(f"{width}x{height}")
    gui = GUI(window, OS)
    gui.start()
    window.mainloop()

if __name__ == "__main__":
    # The following line is to suppress a common warning message by the rdflib package.
    logging.getLogger("rdflib").setLevel(logging.ERROR)
    start_gui()
