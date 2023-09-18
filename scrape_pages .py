'''
Created on Aug 4, 2023

@author: erdem
'''



import os
import pandas as pd
import numpy as np

import json

from time import time
from datetime import datetime

import random
import string
import re


import bs4
from bs4 import BeautifulSoup
from urllib.request import urlopen

from pprint import pprint




LINKS_CSV_FILE="/Users/dicle/Documents/projects/legal_nlp/aym_kararlar_scrape/links.csv"
SCRAPED_LINKS_LIST_FPATH="/Users/dicle/Documents/projects/legal_nlp/scraped_links.txt"


def collect_page_links(url):
    
    page = urlopen(url)
    
    html = page.read().decode("utf-8")
    
    soup = BeautifulSoup(html, "html.parser")
    """
    txt = soup.get_text()
    pprint(txt)
    """
    #links = soup.find_all("a")   #
    
    tag = "a"   #"div"
    class_ =  "waves-effect animsition-link"     #"birkarar col-sm-12"
    links = soup.find_all(tag, class_=class_)
    
    print(set([type(link) for link in links]))
    # some cleaning
    
    texts = [link.text for link in links]
    links = [link.get("href") for link in links]
    
    
    print("texts")
    pprint(texts)
    
    print()
    
    
    print("links")
    pprint(links)
    
    
    return links

def navigate_pages(main_page="https://normkararlarbilgibankasi.anayasa.gov.tr/?page=",
                   outfolder="/Users/dicle/Documents/projects/legal_nlp/ana_mah_kararlar_scrape"):
    
    npages = 396  # npages=396 on the main page as of 4 August 2023
    
    pagenos = list(range(1, npages+1))   
    
    outpath = os.path.join(outfolder, "links.csv")
    
    for pno in pagenos:
        
        link = main_page + str(pno)
        karar_links = collect_page_links(link)
        
        df = pd.DataFrame([{"page_no" : pno, "karar_page_link" : link} for link in karar_links])

        df.to_csv(outpath, mode='a', index=False, sep="\t", header=not os.path.exists(outpath))
        
        print("Listed Page", pno)


def get_meta_info(page_link):
    
    
    page = urlopen(page_link)
    
    html = page.read().decode("utf-8")
    
    soup = BeautifulSoup(html, "html.parser")
    """
    txt = soup.get_text()
    pprint(txt)
    """
    #links = soup.find_all("a")   #
    
    tag = "div"   #"div"
    class_ =  "tab-pane fade"     # "birkarar col-sm-12"
    id_ = "KararDetaylari"
    table_wrapper = soup.find_all(tag, class_=class_)
    table = soup.find("table", class_="table")
    
    print("table")
    pprint(table)
    
    print("type tablewrapper:", type(table_wrapper))
    print("type wr one element:", type(table_wrapper[0]))
    print("type table:", type(table))
    
    
    rows = table.find_all("tr")
    
    row_dicts = []
    
    for row in rows:
        
        cells = row.find_all("td")
        #row_dicts.append({cells[0].text.strip() : cells[1].text})
        row_dicts.append({cells[0].text.strip() : restructure_and_clean_text(cells[1].text)})

    
    print("cells")
    pprint(row_dicts)
    print(len(row_dicts), len(rows))
    
    return row_dicts




def restructure_and_clean_text(text_):
    
    text = text_.strip()
    
    text = text.replace("\xa0", " ")
    text = text.replace("\r\n", " ")
    text = re.sub("\s+", " ", text)
    
    return text


def get_text(page_link):    
    
    
    page = urlopen(page_link)
    
    html = page.read().decode("utf-8")
    
    soup = BeautifulSoup(html, "html.parser")
    """
    txt = soup.get_text()
    pprint(txt)
    """
    #links = soup.find_all("a")   #
    
    tag = "p"   #"div"
    class_ =  "MsoNormal"     #"birkarar col-sm-12"
    paragraphs = soup.find_all(tag, class_=class_)
    
    texts = [link.text for link in paragraphs]
    
    # prep
    texts = [text.replace("\r\n", " ") for text in texts]
    texts = [text.replace("\n", " ") for text in texts]
    texts = [text.strip() for text in texts]
    
    
    txt = "\n".join(texts)
    
    return txt



def read_links_file(path=LINKS_CSV_FILE):
    
    df = pd.read_csv(path, sep="\t")
    links = df["karar_page_link"].tolist()
    return links



def json_to_disc(fpath, obj):
    
    json_obj = json.dumps(obj, indent=2, ensure_ascii=False)
    with open(fpath, "w") as f:
        f.write(json_obj)


def read_json_file(json_path):
    
    f = open(json_path, "r")

    content = json.load(f)
    return content


# return a str like a hash code
def generate_random_str(size_choices=[4,5,6]):
    

    return "".join(random.sample(string.ascii_letters, random.choice(size_choices)))  


def get_current_time_strf():
    
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_file_creation_time_strf(fpath):

    tstr = datetime.fromtimestamp(os.path.getctime(fpath)).strftime('%Y-%m-%d %H:%M:%S')
    return tstr

def get_file_modify_time_strf(fpath):

    tstr = datetime.fromtimestamp(os.path.getmtime(fpath)).strftime('%Y-%m-%d %H:%M:%S')
    return tstr




def add_link_to_scraped_pages(link):
    
    alread_scraped_fpath = SCRAPED_LINKS_LIST_FPATH
    
    with open(alread_scraped_fpath, "a") as f:
        f.write("\n"+link)


def get_already_scraped_links():
    
    alread_scraped_fpath = SCRAPED_LINKS_LIST_FPATH
    links = []
    
    with open(alread_scraped_fpath, "r") as f:
        links = f.readlines()
        links = [link.strip() for link in links if len(link.strip()) > 0]
        
   
    return links


def get_fnames_in_folder(folder_path, ext=".json"):

    fnames = os.listdir(folder_path)
    
    if ext:
        fnames = [fname for fname in fnames if fname.endswith(ext)]
    
    return fnames



def main_add_scrape_time():
    
    folder = "/Users/dicle/Documents/projects/legal_nlp/aym_karar_texts2"
    fnames = get_fnames_in_folder(folder, ext=".json")
    
    outfolder = "/Users/dicle/Documents/projects/legal_nlp/aym_kararlar_final"
    
    for fname in fnames:
        
        jpath = os.path.join(folder, fname)
        
        cdict = read_json_file(jpath)
        create_time = get_file_creation_time_strf(jpath)
        cdict["scrape_time"] = create_time
        
        outjpath = os.path.join(outfolder, fname)
        json_to_disc(outjpath, cdict)
    
    print("Finished modifying ", len(fnames), "files.")
    
    
        
        
        
        

    


def scrape_texts(links=None,
                 outfolder="/Users/dicle/Documents/projects/legal_nlp/aym_karar_texts3",
                 ):
    
    if links is None:
        links = read_links_file()
    
    
    scraped_page_links = get_already_scraped_links()

    nlinks = len(links)
    
    t00 = time()
    for pno, page_link in enumerate(links):
        
        
        if page_link not in scraped_page_links:    # against unwanted repeats after pauses, we check if we had already seen and scraped that link
            
            t0 = time()
            
            content = get_text(page_link)

            row = {}        
            
            row["text"] = content
            row["address"] = page_link
            row["pno"] = pno
        
            txtid1 = "-".join(page_link.split("/")[-2:])
            txtid = txtid1 + "__" + generate_random_str(size_choices=[3,5])
            
            row["id"] = txtid
            
            
            metadata = get_meta_info(page_link)
            
            repeat = 0
            for d in metadata:
                
                newkey = list(d.keys())[0]
                val = d[newkey]
                if newkey not in row.keys():
                    row.update(d)
                else:
                    row[newkey+"_"+str(repeat)] = val
                    repeat += 1
             
             
             
            row["scrape_time"] = get_current_time_strf() 
             
            t1 = time()
            
            duration = round(t1-t0, 3)
            row["duration_for_scraping(sec.)"] = duration
            
                    
            txt_json_path = os.path.join(outfolder, txtid+".json")
            json_to_disc(txt_json_path, row)
            
            add_link_to_scraped_pages(page_link)
            
            print("Finished ", pno, " : ", page_link)
            print("nlinks remained:", nlinks-pno)
            print("Duration for scraping", duration)
            print()
    
    t11 = time()
    print("Finised all.")
    print("Total duration:", round(t11-t00, 3))  
    
    
    


    
    
  
"""    
def scrape_texts_csv(links=None,
                 outfolder="/Users/dicle/Documents/projects/legal_nlp/aym_karar_texts"
                 ):
    
    if links is None:
        links = read_links_file()
    
    
    
    outpath = os.path.join(outfolder, "karar_texts.csv")
    
    nlinks = len(links)
    
    t00 = time()
    for pno, page_link in enumerate(links):
        
        
        
        t0 = time()
        row = {}
        
        content = get_text(page_link)
        
        row["text"] = content
        row["address"] = page_link
        row["pno"] = pno
        
        metadata = get_meta_info(page_link)
        
        if len(metadata) > 0:
            row.update(metadata[0])
            
            for i,d in enumerate(metadata[1:]):
                new_d = {k+"_"+str(i+1) : v for k,v in d.items()}
                row.update(new_d)
        t1 = time()
        
        duration = round(t1-t0, 3)
        row["duration_for_scraping(sec.)"] = duration
                
        df = pd.DataFrame([row])
        df.to_csv(outpath, mode='a', index=False, sep="\t", header=not os.path.exists(outpath))
        
        
        
        print("Finished ", pno, " : ", page_link)
        print("nlinks remained:", nlinks-pno)
        print("Duration for scraping", duration)
        print()
    
    t11 = time()
    print("Finised all.")
    print("Total duration:", round(t11-t00, 3))

"""




def main():

    print()
    
    main_outfolder = "/Users/dicle/Documents/projects/legal_nlp/ana_mah_kararlar_scrape"
    
    df = pd.DataFrame()
    
    
    mainpage = "https://normkararlarbilgibankasi.anayasa.gov.tr/?page="
    #navigate_pages(mainpage)
    
    
    #get_meta_info(page_link="https://normkararlarbilgibankasi.anayasa.gov.tr/ND/2023/94")
    

if __name__ == '__main__':

    """
    addr = "https://normkararlarbilgibankasi.anayasa.gov.tr/ND/2022/163"
    txt = get_text(addr)
    pprint(txt)
    
    d = get_meta_info(addr)
    pprint(d)
    """
    scrape_texts(outfolder="/Users/dicle/Documents/projects/legal_nlp/aym_kararlar_final")

    
    
    