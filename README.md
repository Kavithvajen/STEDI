# STEDI (Support Tool for Ethical Data Integration)

A prototype tool to identify ethical issues that arise due to the integration of linked-data datasets.  

## Steps to run STEDI on your machine:

### Step 1. Install Python 3 (if you don't have it)

**If you installed Python using Homebrew then please re-install the latest version of Python from the official website. This is because the Python distribution available on Homebrew does not come bundled with the Tcl/Tk dependency required by tkinter.**

STEDI was developed and tested with Python 3.8.5 but other versions of Python 3 must work too.

Official Python downloads page: https://www.python.org/downloads/release/python-385/

### Step 2. Create a virtual environment

It is always a good idea to keep the package dependencies required for a single project within a virtual environment. To create a new python environment for this project, **navigate to your desired location** and type the following in your terminal:
```
python3 -m venv STEDI
```

You've successfully created a virtual environment called STEDI. Now you need to activate it and to do that type the following in your terminal:
```
source STEDI/bin/activate
```

More information at: https://docs.python.org/3/library/venv.html

### Step 3. Install application dependencies

First, navigate to where the STEDI application is stored and then type the following in your terminal:
```
pip install -r requirements.txt
```

The "requirements.txt" file contains the names of all the packages the application depends on. Hence, using pip (the default Python package manager) we were able to install all the dependencies in one go! 

### Step 4. Run STEDI

Now that the environment is all setup and ready to go, navigate into `tool/src` from the root directory of the application. Run the tool by typing the following in your terminal:
```
python stedi.py
```

---

## Exiting the virtual environment

Simply type the following in your terminal:
```
deactivate
```

## Uninstallation

**If you do not intend on running the tool after this, you can simply delete the virtual environment folder created in Step 2 and then delete the entire folder containing the STEDI application.**
