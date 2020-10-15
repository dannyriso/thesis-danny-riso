"""
wiki_demo.py

Goal is to develop a program which can access the page and categorylinks
pages extracted from Wikipedia dumps and put them into a list
and then eventually a hierarchy.

Currently, functionality is held up by construction of PAGES_FILE from SQL dump.
"""

"""
# To test with enwiki, larger set
# (https://en.wikipedia.org/wiki/Category:Dog_breeds)
WIKI = "enwiki"
CAT_LINKS_FILE = "enwiki_categorylinks"
PAGES_FILE = "enwiki_page"
DESIRED_CATEGORY = "'Dog_breeds'"
"""

# To test with enwikibooks, smaller set with fewer subcategories
# (https://en.wikibooks.org/wiki/Category:Book:Organic_Chemistry)
WIKI = "enwikibooks"
CAT_LINKS_FILE = "enwikibooks_categorylinks"
PAGES_FILE = "enwikibooks_page"
DESIRED_CATEGORY = "'Book:Organic_Chemistry'"

def main():
    # Setup
    cat_links = open(CAT_LINKS_FILE, 'r')
    pages = open(PAGES_FILE, 'r')
    pages_in_category = []
    
    # Find desired catagory in category links file
    for category in cat_links:
        delim_c1 = category.find('\t')
        delim_c2 = category.find('\t', delim_c1+1)
        
        cat_name = category[delim_c1+1:delim_c2]
        
        # If desired category, find all pages linking to it in pages file
        if cat_name == DESIRED_CATEGORY:
            page_id = category[:delim_c1]
            page_type = category[delim_c2+1:]
            for page in pages:
                delim_p1 = category.find('\t')
                delim_p2 = category.find('\t', delim_p1+1)
                
                p_id = page[:delim_p1+1]
                if page_id == p_id:
                    p_name = page[delim_p1+1:delim_p2+1]
                    pages_in_category.append(p_name)
    
    # Print results
    print("Pages in category", DESIRED_CATEGORY, ":", pages_in_category)
    
    # Clean up
    cat_links.close()
    pages.close()
    

if __name__ == "__main__":
    print("Currently working with", WIKI)
    main()