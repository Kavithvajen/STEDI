import sys
sys.path.append('../tool/')
import tool
import unittest
from unittest import mock
import io

import rdflib
from rdflib.namespace import RDF, OWL
import requests
import json
import sys
import os
import logging
import spacy
import re

class TestMainFunction(unittest.TestCase):

    def runTest(self, return_value, method_to_be_called):
        with mock.patch('builtins.input', return_value=return_value), mock.patch(f'tool.{method_to_be_called}') as mock_patch:
            tool.main()
            self.assertTrue(mock_patch.called)

    def test_positive_main_function(self):
        yes = ("Y", "y", "yes", "Yes", "YES")
        for option in yes:
            self.runTest(option, "start_execution")

    def test_negative_main_function(self):
        no = ("N", "n", "no", "No", "NO")
        for option in no:
            self.runTest(option, "sys.exit")

    def test_else_main_function(self):
        other = ("k", "1", " ", "", "blah", "%", "yn", "Yes No")
        for option in other:
            self.runTest(option, "sys.exit")

#     def test_start_processing(self):
#         os.chdir("../tool/")
#         dataset_name = "TestDataset.owl"
#         dataset_object = tool.Dataset(dataset_name)
#         organisation_name = "Test"
#         ethics_ontology = rdflib.Graph()
#         ethics_ontology.parse("ontology/EthicsOntology.owl", format = rdflib.util.guess_format('ontology/EthicsOntology.owl'))

#         dataset_object.start_processing(organisation_name, ethics_ontology)


if __name__ == '__main__':
    unittest.main()
