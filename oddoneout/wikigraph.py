"""
wikigraph.py

Implements the WCGTaxonomy subclass of the Taxonomy class.

It is intended to access the structure of the Wikipedia Category Graph,
derived from the enwiki categorylinks and pages files,
so it can be ordered into an ontology.
"""

from taxonomy import Taxonomy, Specificity
from wiki_demo import findPagesInCategory, findPagesById


class WCGTaxonomy(Taxonomy):
    
    def __init__(self, categorylinks_filename, pages_filename):
        self.specificity = Specificity()
        self.catlinks = categorylinks_filename
        self.pages = pages_filename
        self.cat_name_list = []
        self.page_name_list = self.get_descendant_instances(self.get_root())
        self.num_insts = len(self.page_name_list)
        
    def is_instance(self, node):
        return node in self.page_name_list and self.specificity(self, node) == 0
    
    def is_category(self, node):
        return node in self.cat_name_list and self.specificity(self, node) > 0
    
    def num_instances(self):
        return self.num_insts
    
    def get_root(self):
        # For now, use "'Recipes'" as a guaranteed root with many subcategories.
        # When looking at the entire enwikibooks, use "'Categories'"
        return "'Recipes'"
    
    def get_ancestor_categories(self, node):
        # Given a page label, returns a set of its ancestor category labels
        # !!!! Current priority !!!!
        # Only returns direct parents right now, not further ancestors
        page_file = open(self.pages)
        for page in page_file:
            page_id, page_namespace, page_title, page_is_redirect, page_len, page_content_model, page_lang = page.split('\t')
            if page_title == node:
                break
            
        page_file.close()
        return getCategoriesOfPage(self.get_root(), self.catlinks, page_id)
    
    def get_descendant_instances(self, node):
        # Given a category label, returns a set of its descendant page labels
        descendants = set()
        categories = [node]
        while(len(categories) != 0):
            category = categories.pop()
#            print(len(categories), "categories left to search.")
#            print("Current cat:", category)
            page_ids, subcat_ids, file_ids = findPagesInCategory(self.catlinks, category)
            pages = findPagesById(self.pages, page_ids)
            subcats = findPagesById(self.pages, subcat_ids)
#            print("PAGES:", [page for page in pages])
#            print("SUBCATS:", [cat for cat in subcats])
            for page_title in pages:
                descendants.add(page_title)
            for cat in subcats:
                if cat not in self.cat_name_list:
                    categories.append(cat)
                    self.cat_name_list.append(cat)
        return descendants


def getCategoriesOfPage(root, catlinks_filename, p_id):
    catlinks_file = open(catlinks_filename, 'r')
    
    categories = set()
    for category in catlinks_file:
        page_id, cat_label, page_type = category.strip('\n').split('\t')
        if page_id == p_id:
            categories.add(cat_label)
    
    catlinks_file.close()
    return categories

