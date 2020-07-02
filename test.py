from rdflib import Graph, Literal, RDF, URIRef
# rdflib knows about some namespaces, like FOAF
from rdflib.namespace import FOAF , XSD

# create a Graph
g = Graph()

# Create an RDF URI node to use as the subject for multiple triples
donna = URIRef("http://example.org/donna")

# Add triples using store's add() method.
g.add((donna, RDF.type, FOAF.Person))
g.add((donna, FOAF.nick, Literal("donna", lang="ed")))
g.add((donna, FOAF.name, Literal("Donna Fales")))
g.add((donna, FOAF.mbox, URIRef("mailto:donna@example.org")))

# Add another person
ed = URIRef("http://example.org/edward")

#Add triples using store's add() method.
g.add((ed, RDF.type, FOAF.Person))
g.add((ed, FOAF.nick, Literal("ed", datatype=XSD.string)))
g.add((ed, FOAF.name, Literal("Edward Scissorhands")))
g.add((ed, FOAF.mbox, URIRef("mailto:e.scissorhands@example.org")))


# Bind the FOAF namespace to a prefix for more readable output
g.bind("foaf", FOAF)

# print all the data in the Notation3 format
print("--- printing mboxes ---")
print(g.serialize(format='n3').decode("utf-8"))

for s, p, o in g.triples((None,  RDF.type, None)):
    print("{} is a {}".format(s, o))
    print(f"Label: {g.preferredLabel(s)}")

for person in g.subjects(RDF.type, FOAF.Person):
    print("{} is a person".format(person))

print(g.value(ed, FOAF.name)) # get any name of bob
# get the one person that knows bob and raise an exception if more are found
print(g.value(predicate = FOAF.name, object=ed, any=False))

print(iter(g))

########################


# from __future__ import print_function
# import sys
# import rdflib
# from rdflib import URIRef, Namespace, RDF, Graph, Literal, BNode, plugin, Variable
# from optparse import OptionParser
# # given a subject uri and a string for a schema.org predicate,
# # return a list of any matching objects
# # representing the object by its name property if available,
# # otherwise representing the object by its uri
# #graph = rdflib.Graph()
# def get_labels(graph, uri, predicate_string):
#     predicate = rdflib.term.URIRef(u'http://schema.org/'+predicate_string)
#     name = rdflib.term.URIRef(u'http://schema.org/name')
#     object_list = []
#     print(f"Graph objects: {list(graph.objects(uri, predicate))}")
#     for obj in graph.objects(uri, predicate):
#         print(f"\nObject: {obj}\n\n")
#         print(f"Label: {graph.label(uri)}")
#         label = obj
#         print(f"\nGraph value: {graph.value(obj, name)}\n\n")
#         if graph.value(obj, name):
#             label = graph.value(obj, name)
#         object_list.append(label)
#     object_labels = ('\n'.join(object_list))
#     return(object_labels)
# #if __name__ == "__main__":
# def main():
#     # set default uri and predicates
#     uri = rdflib.term.URIRef(u'http://www.worldcat.org/oclc/82671871')
#     predicates_delimited = "name,creator,description,about"
#     # look for uri and predicates parameters that over-ride the defaults
#     # parser = OptionParser()
#     # parser.add_option("-u", dest="uri", help="The URI of the RDF resource", action='store')
#     # parser.add_option("-p", dest="predicates_delimited",
#     # help="A comma-separated list of predicates to list, e.g., name,creator,contributor,about",
#     # action='store')
#     # (options, args) = parser.parse_args(sys.argv)
#     # if options.uri:
#     #   uri = rdflib.term.URIRef(options.uri)
#     # if options.predicates_delimited:
#     #   predicates_delimited = options.predicates_delimited
#     predicates = predicates_delimited.split(",")
#     # create an in-memory RDF graph for the resource named in uri
#     graph = rdflib.Graph()
#     graph.parse(uri)
#     # for each of the strings in the predicates list ...
#     for predicate_string in predicates:
#         # get a label(s) for any object(s) in the graph for the predicate
#         print(get_labels(graph,uri,predicate_string))
# if __name__ == "__main__":
#     main()

# ###############
