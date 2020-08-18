# STEDI (Support Tool for Ethical Data Integration)

## Quick Introduction

This tool was built as part of my dissertation for the degree M.Sc. Computer Science at Trinity College Dublin and is supervised by Prof. Declan O'Sullivan. The goal of this prototype tool is to demonstrate a method for preventing ethical issues that could arise during the integration of two or more datasets. This tool is currently focussed on working with linked-data datasets and hence uses some NLP techniques to identify issue-causing areas in the vocabularies and predicates of the datasets.

## Steps to run STEDI:

### Step 1. Install Python 3

**If you installed Python 3 using Homebrew, then please re-install the latest version of Python from the official website because the Python distribution available on Homebrew does not come bundled with the Tcl/Tk dependency required by tkinter.**

STEDI was developed and tested with Python 3.8.5, but other versions of Python 3 must work too.

Official release page: https://www.python.org/downloads/release/python-385/

### Step 2. Create a virtual environment

It is always a good idea to keep the package dependencies required for a single project within a virtual environment. To create a new python environment for this project, **navigate to your desired location** and type the following in your terminal:
```
python3 -m venv STEDI
```

You've successfully created a virtual environment called STEDI. Now you need to activate it and to do that type the following in your terminal:
```
source STEDI/bin/activate
```

> After running the tool, if you wish to **exit the virtual environment**, type `deactivate` in your terminal.

More information at: https://docs.python.org/3/library/venv.html

### Step 3. Download application

You can either `git clone` the repository to your preferred location or simply download the zip file and unpack it at your preferred location.

### Step 4. Install application dependencies

First, navigate to where the STEDI application is stored and then type the following in your terminal:
```
pip install -r requirements.txt
```

The "requirements.txt" file contains the names of all the packages the application depends on. Hence, using pip (the default Python package manager), we were able to install all the dependencies in one go!

### Step 5. Run STEDI

Now that the environment is all set up and ready to go, run the tool by typing the following in your terminal:
```
cd src
python stedi.py
```
---

## Uninstallation

If you do not intend on running STEDI after this, you can delete the virtual environment folder created in Step 2 and then remove the entire folder containing the STEDI application.

---
