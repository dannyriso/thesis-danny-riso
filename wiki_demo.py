"""
wiki_demo.py

This code accesses the page and categorylinks files extracted from
Wikipedia dumps (using Wikiextractor and WikiUtils github repos) and
puts the titles of all pages linked to by a certain category into a list,
then returns the list.
"""

# To test with enwiki, finding all Dog Breed pages:
# (https://en.wikipedia.org/wiki/Category:Dog_breeds)
WIKI = "enwiki"
CAT_LINKS_FILE = "enwiki_categorylinks"
PAGES_FILE = "enwiki_page"
DESIRED_CATEGORY = "'Dog_breeds'"

"""
# To test with enwikibooks, smaller set with fewer subcategories:
# (https://en.wikibooks.org/wiki/Category:Book:Organic_Chemistry)
WIKI = "enwikibooks"
CAT_LINKS_FILE = "enwikibooks_categorylinks"
PAGES_FILE = "enwikibooks_page"
DESIRED_CATEGORY = "'Book:Organic_Chemistry'"
"""

def main():
    # Setup
    cat_links = open(CAT_LINKS_FILE, 'r')
    pages = open(PAGES_FILE, 'r')
    pages_in_category = []
    page_ids = []
    subcats = []
    
    # Find instances of desired catagory in categorylinks file
    for category in cat_links:
        delim_c1 = category.find('\t')
        delim_c2 = category.find('\t', delim_c1+1)
        delim_c3 = category.find('\t\n', delim_c2+1)
        
        cat_name = category[delim_c1+1:delim_c2]
        
        # If desired category, find all page_ids it links to
        if cat_name == DESIRED_CATEGORY:
            page_id = category[:delim_c1]
            file_type = category[delim_c2+1:delim_c3]
            if file_type == "'page'":
                page_ids.append(page_id)
            elif file_type == "'subcat'":
                subcats.append(page_id)
    
    # For each found page_id, locate it in the pages file and add it
    # to the list to return.
    for page in pages:
        delim_p1 = page.find('\t')
        p_id = page[:delim_p1]
        
        if p_id in page_ids:
            delim_p2 = page.find('\t', delim_p1+1)
            delim_p3 = page.find('\t', delim_p2+1)
            p_label = page[delim_p2+1:delim_p3]
            pages_in_category.append(p_label)
            page_ids.remove(p_id)
    
    # Print results for debugging and clarity
    print("Pages in category", DESIRED_CATEGORY, ":")
    for p in pages_in_category:
        print(p)
    
    # Clean up
    cat_links.close()
    pages.close()
    return pages_in_category

if __name__ == "__main__":
    print("Currently working with", WIKI)
    main()