import rdflib

g = rdflib.Graph()
dataset = "TestDataset.owl"
g.parse(f"../tool/input/{dataset}", format = rdflib.util.guess_format(f"../tool/input/{dataset}"))

qres = g.query(
    """
    SELECT ?p
    WHERE {
        ?s ?p ?o .
    }
    """)

for x in qres:
    print (f"X: {x}")
