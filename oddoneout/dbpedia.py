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
        # self.num_insts = len(self.get_descendant_instances(self.get_root()))
        # This takes at least 48 hours to fully calculate,
        # and monopolizes a lot of DBpedia's queryability.
        self.num_insts = 6232635
        # This is the number of articles on Wikipedia as of 21 Jan 2021
        self.ancestors = defaultdict(list)
        self.children = defaultdict(list)
    
    
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
            print ("Query failed.")
            return None
    
    
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
            print ("Query failed.")
            return None


    def get_root(self):
        return "Contents"


    def num_instances(self):
        return self.num_insts


    def get_ancestor_categories(self, node_name):
        if node_name in self.ancestors:
            return self.ancestors[node_name]
        elif node_name == self.get_root():
            return []
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
                for trip in triples['results']['bindings']:
                    if trip['label']['value'] not in self.ancestors[node_name]:
                        for anc in self.get_ancestor_categories(trip['label']['value']):
                            if anc not in self.ancestors[node_name]:
                                self.ancestors[node_name].append(anc)
                        self.ancestors[node_name].append(trip['label']['value'])
                
            except:
                print ("Query failed for ancestors of", node_name)
        
        return self.ancestors[node_name]


    def get_descendant_instances(self, node_name):
        categories = [node_name.replace(' ', '_')]
        instances = []
        for cat in categories:
            if cat in self.children:
                for c in self.children[cat]:
                    if self.is_category(c) and c not in categories:
                        categories.append(c)
            else:
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
                        if trip['label']['value'].replace(' ', '_') not in categories:
                            categories.append(trip['label']['value'].replace(' ', '_'))
                    
                except:
                    print ("Query failed for subcategories of", cat)
        
#        print("Got subcats, now get instances.")
        for cat in categories:
            if cat in self.children:
                for c in self.children[cat]:
                    if self.is_instance(c) and c not in instances:
                        instances.append(c)
            else:
                query = self.db_prefixes + """
                    SELECT ?label
                    WHERE {
                        ?resource dct:subject <http://dbpedia.org/resource/Category:""" + cat + """>;
                        rdfs:label ?label
                        
                        FILTER(lang(?label) = 'en')
                    }
                """
                self.sparql.setQuery(query)
                try:
                    self.sparql.setReturnFormat(JSON)
                    results = self.sparql.query()
                    triples = results.convert()
                    for trip in triples['results']['bindings']:
                        if trip['label']['value'] not in instances:
                            instances.append(trip['label']['value'])
                    
                except:
                    print ("Query failed for instances of ", cat)
        
#        print (instances)
        return instances
    