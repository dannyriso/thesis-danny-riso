"""
dbpedia.py

Implements the DBPediaTaxonomy subclass of the Taxonomy class.

It is intended to access the structure of the DBPedia database 
so it can be ordered into an ontology.
"""

from taxonomy import Taxonomy, Specificity
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import defaultdict


class DBpediaTaxonomy(Taxonomy):
    
    def __init__(self):
        self.specificity = Specificity()
        self.db_prefixes = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dct: <http://purl.org/dc/terms/>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX dbr: <http://dbpedia.org/resource/>
            PREFIX dbc: <http://dbpedia.org/resource/Category>
        """
        self.sparql = SPARQLWrapper("https://dbpedia.org/sparql")
        self.ancestors = defaultdict(set)
        self.descendants = defaultdict(set)
        # self.num_insts = len(self.get_descendant_instances(self.get_root()))
        # This takes at least 48 hours to fully calculate,
        # and monopolizes a lot of DBpedia's queryability.
        self.num_insts = 52793963
        # 52,793,963 is the number of wiki pages on Wikipedia as of 25 Feb 2021
    
    
    def is_instance(self, node_name):
        query = self.db_prefixes + """
        ASK {
            ?resource rdfs:label \"""" + node_name + """\"@en;
            dct:subject ?subject
        }
        """
        #print ("Generated query:", query)
        self.sparql.setQuery(query)
        try:
            self.sparql.setReturnFormat(JSON)
            results = self.sparql.query()
            triples = results.convert()
            #print ("Result:", triples['boolean'])
            return triples['boolean']
        except:
            print ("Query failed; instance check failed for", node_name)
    
    
    def is_category(self, node_name):
        query = self.db_prefixes + """
        ASK {
            ?resource rdfs:label \"""" + node_name + """\"@en;
            rdf:type skos:Concept
        }
        """
        #print ("Generated query:", query)
        self.sparql.setQuery(query)
        try:
            self.sparql.setReturnFormat(JSON)
            results = self.sparql.query()
            triples = results.convert()
            #print ("Result:", triples['boolean'])
            return triples['boolean']
        except:
            print ("Query failed; category check failed for", node_name)


    def get_root(self):
        return "Contents"


    def num_instances(self):
        return self.num_insts


    def get_ancestor_categories(self, node_name):
        #print("Getting ancestors of", node_name)
        if node_name in self.ancestors:
            return self.ancestors[node_name]
        elif node_name == self.get_root():
            return set()
        else:
            if self.is_category(node_name):
                query = self.db_prefixes + """
                SELECT ?label
                WHERE {
                    ?resource rdfs:label \"""" + node_name + """\"@en;
                    skos:broader ?subject.
                    ?subject rdfs:label ?label
                }
                """
            else:
                query = self.db_prefixes + """
                SELECT ?label
                WHERE {
                    ?resource rdfs:label \"""" + node_name + """\"@en;
                    dct:subject ?subject.
                    ?subject rdfs:label ?label
                }
                """
            self.sparql.setQuery(query)
            try:
                self.sparql.setReturnFormat(JSON)
                results = self.sparql.query()
                triples = results.convert()
                for res in triples['results']['bindings']:
                    res_label = res['label']['value']
                    if res_label not in self.ancestors[node_name]:
                        for anc in self.get_ancestor_categories(res_label):
                            if anc not in self.ancestors[node_name]:
                                self.ancestors[node_name].add(anc)
                        self.ancestors[node_name].add(res_label)
                
            except:
                print ("Query failed for ancestors of", node_name)
                self.ancestors.pop(node_name)
        
        return set(self.ancestors[node_name])


    def get_descendant_instances(self, node_name):
        category_name = node_name.replace(' ', '_').replace('"', '\"')
        categories = [category_name]
        visited_categories = set()
        instances = []
        while(categories):
            cat = categories.pop()
            visited_categories.add(cat)
            #print("Get descendants of", cat)
            
            if cat in self.descendants:
                 for inst in self.descendants[cat]:
                     self.descendants[category_name].add(inst)
            elif self.is_instance(cat):
                self.descendants[cat] = set(cat)
                self.descendants[category_name].add(cat)
            else:
                instances = self.db_prefixes + """
                    SELECT ?label
                    WHERE {
                        ?resource dct:subject <http://dbpedia.org/resource/Category:""" + cat + """>;
                        rdfs:label ?label
                        
                        FILTER(lang(?label) = 'en')
                    }
                """
                self.sparql.setQuery(instances)
                try:
                    self.sparql.setReturnFormat(JSON)
                    results = self.sparql.query()
                    triples = results.convert()
                    for trip in triples['results']['bindings']:
                        instance_name = trip['label']['value']
                        self.descendants[category_name].add(instance_name)
                    
                except:
                    print ("Query failed for instances of", cat)
                    if cat in self.descendants:
                        self.descendants.pop(cat)
        
        
                subcats = self.db_prefixes + """
                    SELECT ?label
                    WHERE {
                        ?resource skos:broader <http://dbpedia.org/resource/Category:""" + cat + """>;
                        rdfs:label ?label
                        
                        FILTER(lang(?label) = 'en')
                    }
                """
                self.sparql.setQuery(subcats)
                try:
                    self.sparql.setReturnFormat(JSON)
                    results = self.sparql.query()
                    triples = results.convert()
                    for trip in triples['results']['bindings']:
                        subcategory_name = trip['label']['value'].replace(' ', '_').replace('"', '\"')
                        if subcategory_name not in visited_categories:
                            categories.append(subcategory_name)
                    
                except:
                    print ("Query failed for subcategories of ", cat)
                    if cat in self.descendants:
                        self.descendants.pop(cat)
        
        return self.descendants[category_name]
        