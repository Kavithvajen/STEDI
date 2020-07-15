import requests
import json
import rdflib
import os

URL = "https://lov.linkeddata.es/dataset/lov/api/v2/vocabulary/info?"

dataset_list = [f for f in os.listdir("Input") if not f.startswith(".")]
graph_list = []

for dataset in dataset_list:
    graph_list.append(rdflib.Graph())
    graph_list[-1].parse(f"Input/{dataset}", format = rdflib.util.guess_format(f"/Input/{dataset}"))
    graph_list[-1].serialize(format="xml")

    for vocab in graph_list[-1].namespace_manager.namespaces():
        print(vocab[0])
        PARAMS = {"vocab" : vocab[0]}

        try:
            response = requests.get(url = URL, params = PARAMS)
            response.raise_for_status()
            print(response)
        except requests.exceptions.HTTPError as e:
            if response.status_code == 503:
                print(f"The vocabulary API service is temporarily down. The program will continue in offline mode!")
            else:
                print(f"There seems to be some unknown error with the API. The program will still continue in offline mode! \nError message received from server: \n{e}")
        except Exception as e:
            print(f"There seems to be an unexpected error. Quitting program for now. Copy the error message displayed below and contact your system administrator!\n{e}")


        #data = response.json()

# try:
#     response = requests.get(url = URL, params = PARAMS)
#     data = response.json()

# except Exception as e:
# #except requests.exceptions.RequestException as e:
#         print(f"\nThere's some issue, possibly a network issue. \n Here's the error: \n{e}\n\nTool will continue in offline mode!")

# print("it went through!")
