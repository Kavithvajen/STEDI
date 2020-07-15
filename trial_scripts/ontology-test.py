import rdflib
from rdflib.namespace import RDF, OWL
import os

#os.chdir("Ontology")
#ontology = "/Users/kavith/Kavith/University/TCD/Dissertation/Development/Dissertation/Ontology/EthicsOntology.owl"

ont_graph = rdflib.Graph()
ont_graph.parse("Ontology/EthicsOntology.owl", format = rdflib.util.guess_format('/Ontology/EthicsOntology.owl'))
print("Parsed")

# for s, p, o in ont_graph:
#     print(f"\nSUBJECT: {s}\nPREDICATE: {p}\nOBJECT: {o}\n")

#one = rdflib.URIRef("https://www.scss.tcd.ie/~kamarajk/EthicsOntology#one")
n = rdflib.Namespace("https://www.scss.tcd.ie/~kamarajk/EthicsOntology#")

ont_graph.add((n.one, RDF.type, OWL.NamedIndividual))

for p,o in ont_graph.predicate_objects(n.one):
    print("IN")
    print(f"\nSUBJECT: {n.one}\nPREDICATE: {p}\nOBJECT: {o}\n")

print("Writing to a file")

ont_graph.serialize(destination='output.owl', format='xml')

print("Done")
