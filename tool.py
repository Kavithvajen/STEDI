import rdflib
import requests, json
import sys, os, logging

def checkVocab(vocab):
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

    for tag in data["tags"]:
        if tag == "Geography":
            print("\nNOTE: This dataset probably contains location related data as it uses the {} namespace!".format(data["prefix"]))
        elif tag == "Society":
            print("\nNOTE: This dataset probably contains society related data as it uses the {} namespace!".format(data["prefix"]))
        elif tag == "People":
            print("\nNOTE: This dataset probably contains people related data as it uses the {} namespace!".format(data["prefix"]))
        elif tag == "Health":
            print("\nNOTE: This dataset probably contains health related data as it uses the {} namespace!".format(data["prefix"]))
        elif tag == "Biology":
            print("\nNOTE: This dataset probably contains biology related data as it uses the {} namespace!".format(data["prefix"]))
        elif tag == "Government":
            print("\nNOTE: This dataset probably contains government related data as it uses the {} namespace!".format(data["prefix"]))
        elif tag == "Environment":
            print("\nNOTE: This dataset probably contains environment related data as it uses the {} namespace!".format(data["prefix"]))
        else:
            pass

def loadDatasets():
    os.chdir("Input")
    datasetList = os.listdir()

    graphList = []

    for dataset in datasetList:
        graphList.append(rdflib.Graph())
        graphList[-1].parse(dataset, format = rdflib.util.guess_format("/"+dataset))
        print("\nSuccessfully loaded the \"{}\" dataset. \nNow checking the vocabulary used in the dataset to find potential issues.".format(dataset))
        for vocab in graphList[-1].namespace_manager.namespaces():
            checkVocab(vocab[0])

def main():

    #The following line is to suppress a common warning message by the rdflib package.
    logging.getLogger("rdflib").setLevel(logging.ERROR)

    option = input("\nStarted the tool successfully. Are all the input datasets in the \"Input\" folder? [Y/N]: ")
    if option == "Y" or option == "y":
        loadDatasets()
    elif option == "N" or option == "n":
        print("Okay! Make sure all the input datasets are in the \"Input\" folder and then start the tool.")
        sys.exit()
    else:
        print("Wrong option. Aborting program!")
        sys.exit()

    print("\nTool finished running.")

if __name__ == "__main__":
    main()
