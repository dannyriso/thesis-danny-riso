"""
Tests dbpedia.py, which creates a taxonomy based on the online DBpedia resource.
"""

import unittest
from dbpedia import DBpediaTaxonomy
from taxonomy import lowest_common_ancestor
from solver import solve_puzzle, TaxonomySimilarity, solve_puzzles, silent_logger
from puzzle import OddOneOutPuzzle, common2_puzzles


class TestDBpedia(unittest.TestCase):

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
        expected = ['Contents', 'Wikipedia administration',
                    'Wikipedia administration by MediaWiki feature',
                    'Wikipedia namespace administration', 'Wikipedia namespaces']
        assert sorted(result) == expected

    def test_ancestor_categories2(self):
        result = self.taxonomy.get_ancestor_categories("Food and drink")
        expected = ['Academia', 'Academic discipline interactions',
                    'Academic disciplines', 'Anthropology', 'Applied disciplines',
                    'Applied sciences', 'Art and culture WikiProjects', 'Articles',
                    'Articles by WikiProject', 'Biology', 'Branches of biology',
                    'Branches of philosophy', 'Branches of science',
                    'Categories by field', 'Categories by parameter',
                    'Categories by topic', 'Categories requiring diffusion', 'Concepts',
                    'Concepts by field', 'Concepts in metaphysics', 'Consciousness',
                    'Container categories', 'Contents', 'Culture',
                    'Culture Wikipedia administration', 'Education', 'Entities',
                    'Euthenics', 'Food Watchlist Articles', 'Food and drink WikiProjects',
                    'Health', 'Health sciences', 'Human activities', 'Human nature',
                    'Humanities', 'Life', 'Life sciences', 'Main topic classifications',
                    'Maintenance by namespace', 'Matter', 'Metaphysics',
                    'Metaphysics of mind', 'Mind', 'Namespace-specific categories',
                    'Natural sciences', 'Nature', 'Neuroscience', 'Objects', 'Ontology',
                    'Organisms', 'Pages by WikiProject', 'Personal life',
                    'Philosophical concepts', 'Philosophy', 'Philosophy by topic',
                    'Philosophy of mind', 'Physical objects', 'Psychological concepts',
                    'Psychology', 'Reality', 'Science', 'Science and technology', 'Self',
                    'Social sciences', 'Society', 'Subfields by academic discipline',
                    'Talk namespace categories', 'Universe', 'WikiProject Food and drink',
                    'WikiProject Food and drink articles', 'WikiProject resources',
                    'WikiProjects', 'WikiProjects by topic', 'Wikipedia administration',
                    'Wikipedia administration by MediaWiki feature',
                    'Wikipedia administration by topic', 'Wikipedia categories',
                    'Wikipedia categories that should not contain articles',
                    'Wikipedia categorization', 'Wikipedia category maintenance',
                    'Wikipedia collaborations', 'Wikipedia content administration',
                    'Wikipedia maintenance', 'Wikipedia namespace administration',
                    'Wikipedia namespaces', 'Wikipedia navigation']
        assert sorted(result) == expected

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
        """
        The first few calls to get_ancestor_categories warms up the
        taxonomy cache, making ancestors of a certain node easy to query
        so that calling lowest_common_ancestor takes less time,
        leaving less room for error due to the DBpedia endpoint being
        busy or Internet shorting out.
        
        This is common among all the test_lowest_common_ancestor methods.
        """
        self.get_ancestor_categories("Main topic classifications")
        self.get_ancestor_categories("Science")
        self.get_ancestor_categories("Mind")
        self.get_ancestor_categories("Vision")
        self.get_ancestor_categories("Light")
        self.get_ancestor_categories("Colors")
        self.get_ancestor_categories("Anatomy")
        self.get_ancestor_categories("Branches of botany")
        self.get_ancestor_categories("Fruit")
        result = lowest_common_ancestor(self.taxonomy,
                                        ["Yellow", "Red", "Green", "Blue"],
                                        "Apple")
        print("Lowest common ancestor 1:", result)
        assert result == (168, "Rainbow colors")

    def test_lowest_common_ancestor2(self):
        self.get_ancestor_categories("Main topic classifications")
        self.get_ancestor_categories("Science")
        self.get_ancestor_categories("Mind")
        self.get_ancestor_categories("Vision")
        self.get_ancestor_categories("Light")
        self.get_ancestor_categories("Colors")
        result = lowest_common_ancestor(self.taxonomy,
                                        ["Yellow", "Red", "Green", "Blue"],
                                        "Cyan")
        print("Lowest common ancestor 2:", result)
        assert result == (104999, "Contents")

    def test_lowest_common_ancestor3(self):
        self.get_ancestor_categories("Main topic classifications")
        self.get_ancestor_categories("Science")
        self.get_ancestor_categories("Anthropology")
        self.get_ancestor_categories("Biology")
        self.get_ancestor_categories("Species")
        self.get_ancestor_categories("Dogs")
        result = lowest_common_ancestor(self.taxonomy,
                                        ["Poodle", "Irish Water Spaniel",
                                         "Wetterhoun", "Lagotto Romagnolo"],
                                        "Golden Retriever")
        print("Lowest common ancestor 3:", result)
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

