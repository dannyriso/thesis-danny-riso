"""
Tests dbpedia.py, which creates a taxonomy based on the online DBpedia resource.
"""

import unittest
from dbpedia import DBpediaTaxonomy
from taxonomy import lowest_common_ancestor
from solver import solve_puzzle, TaxonomySimilarity, solve_puzzles, silent_logger
from puzzle import OddOneOutPuzzle, common2_puzzles


class TestWordnet(unittest.TestCase):

    def setUp(self):
        self.taxonomy = DBpediaTaxonomy()

    def test_is_instance(self):
        assert self.taxonomy.is_instance("Pear")
        assert self.taxonomy.is_instance("Rambutan")
        assert not self.taxonomy.is_instance("Edible fruits")
        assert not self.taxonomy.is_instance("Misspeling")

    def test_is_category(self):
        assert self.taxonomy.is_category("Edible fruits")
        assert self.taxonomy.is_category("Dogs")
        assert not self.taxonomy.is_category("Dog")
        assert not self.taxonomy.is_category("Doggo")

    def test_ancestor_categories1(self):
        result = self.taxonomy.get_ancestor_categories("Articles")
        expected = ["Contents", "Wikipedia namespaces",
                    "Wikipedia namespace administration",
                    "Wikipedia administration by MediaWiki feature",
                    "Wikipedia administration"]
        assert sorted(result) == expected

    def test_ancestor_categories2(self):
        result = self.taxonomy.get_ancestor_categories("Fresh food")
        expected = ["Articles", "Container categories", "Contents", "Food and drink",
                    "Main topic articles", "Main topic classifications",
                    "Wikipedia administration",
                    "Wikipedia administration by MediaWiki feature",
                    "Wikipedia categories",
                    "Wikipedia categories that should not contain articles",
                    "Wikipedia categorization", "Wikipedia content administration",
                    "Wikipedia namespace administration", "Wikipedia namespaces",
                    "Wikipedia navigation"]
        assert sorted(result) == expected
        #assert result == expected
        #print(self.taxonomy.num_instances())

    def test_descendant_instances1(self):
        result = self.taxonomy.get_descendant_instances("Pear dishes")
        expected = ["Birnen, Bohnen, und Speck", "Birnbrot", "Kletzenbrot",
                    "Pear-syrup candy", "Poire à la Beaujolaise", "Poire belle Hélène"]
        assert sorted(result) == expected

    def test_descendant_instances2(self):
        result = self.taxonomy.get_descendant_instances("Water dogs")
        expected = ["American Water Spaniel", "Barbet (dog)", "Cantabrian Water Dog",
                    "English Water Spaniel", "Irish Water Spaniel", "Lagotto Romagnolo",
                    "Poodle", "Portuguese Water Dog", "Spanish Water Dog",
                    "Tweed Water Spaniel", "Water dog", "Wetterhoun"]
        assert sorted(result) == expected
        
    def test_lowest_common_ancestor1(self):
        result = lowest_common_ancestor(self.taxonomy,
                                        ["Orange", "Red", "Green", "Blue"],
                                        "Apple")
        assert result == (168, "Rainbow colors")

    def test_lowest_common_ancestor2(self):
        result = lowest_common_ancestor(self.taxonomy,
                                        ["Orange", "Red", "Green", "Blue"],
                                        "Gold")
        assert result == (104999, "Contents")

    def test_lowest_common_ancestor3(self):
        result = lowest_common_ancestor(self.taxonomy,
                                        ["Poodle", "Irish Water Spaniel",
                                         "Wetterhoun", "Lagotto Romagnolo"],
                                        "Golden Retriever")
        assert result == (4, "Water dogs")

    def test_solve_puzzle(self):
        similarity = TaxonomySimilarity(self.taxonomy)
        puzzle = OddOneOutPuzzle("Golden Retriever",
                                 ["Poodle", "Irish Water Spaniel",
                                  "Wetterhoun", "Lagotto Romagnolo"],
                                 "Water dogs")
        result = solve_puzzle(puzzle, similarity)
        assert result == (0.25, "Water dogs", "Golden Retriever")

    def test_solve_puzzles(self):
        similarity = TaxonomySimilarity(self.taxonomy)
        result = solve_puzzles(common2_puzzles, similarity, logger=silent_logger)
        assert result == (38, 14, 50)


