"""
download.py

Downloads relevant Wikipedia dumps (enwiki and enwikibooks) 
and converts them to text files using the WikiUtils GitHub repo.
The files downloaded and extracted here are utilized in wiki_demo.py,
which converts the text files to ontologies.
"""

import requests # requests.get, for downloading wiki dumps
import subprocess # subprocess.Popen, for running the extraction commands
from pathlib import Path # for checking if a file already exists in pwd

# Initialize dump variables
dump_date = "20201020"
dumps_to_download = [
    "enwiki-" + dump_date + "-page.sql.gz",
    "enwiki-" + dump_date + "-categorylinks.sql.gz",
    "enwikibooks-" + dump_date + "-page.sql.gz",
    "enwikibooks-" + dump_date + "-categorylinks.sql.gz"]

def download():
    wikidumps_url = "https://dumps.wikimedia.org"
    
    for dump in dumps_to_download:
        # First check if dump is already downloaded
        if not Path(dump).is_file():
                        
            # Form the URL of the dump to download and issue request to it
            wiki = dump[:dump.find('-')]
            dump_url = wikidumps_url + "/" + wiki + "/" + dump_date + "/" + dump
            dump_contents = requests.get(dump_url, stream=True)
            
            # Write dump to file
            with open(dump, "wb") as dump_file:
                for chunk in dump_contents.iter_content(chunk_size=1024):
                    if chunk:
                        dump_file.write(chunk)

def extract():
    # Initialize extraction variables
    extracted_files = [
        "enwiki_page",
        "enwiki_categorylinks",
        "enwikibooks_page",
        "enwikibooks_categorylinks"]
    
    for i in range(len(extracted_files)):
        file = extracted_files[i]
        filetype = file[file.find("_")+1:]
        dump = dumps_to_download[i]
        # Check if files have already been extracted
        if not Path(extracted_files[i]).is_file():
            # Extract into text file using WikiUtils repo
            proc = subprocess.Popen(["python", "WikiUtils/parse_mysqldump.py", dump, filetype, file])
            proc.wait()

if __name__ == "__main__":
    download()
    extract()