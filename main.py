from utils import *
import warnings
import os
import json

title_sentences = []
title_sentences.append(("Citation ID","Location ID", "Citing Article Title", "Referenced Paper Title", "Citation Context", "Citation Function", "Citation Polarity"))

def parse_target_group(file_name_without_extension):
    if file_name_without_extension == 'ERA5-Land':
        referenced_title = "Era5-land: a state-of-the-art global reanalysis dataset for land applications"
        referenced_author = "Munoz-Sabater"
        referenced_doi = "10.5194/essd-13-4349-2021"
        published_year = "2021"
    elif file_name_without_extension == 'gcb2015':
        referenced_title = "Global carbon budget 2015"
        referenced_author = "Quéré"
        referenced_doi = "10.5194/essd-7-349-2015"
        published_year = "2015"
    elif file_name_without_extension == 'gcb2016':
        referenced_title = "Global carbon budget 2016"
        referenced_author = "Quéré"
        referenced_doi = "10.5194/essd-8-605-2016"
        published_year = "2016"
    elif file_name_without_extension == 'gcb2018':
        referenced_title = "Global carbon budget 2018"
        referenced_author = "Quéré"
        referenced_doi = "10.5194/essd-10-2141-2018"
        published_year = "2018"
    elif file_name_without_extension == 'gcb2019':
        referenced_title = "Global carbon budget 2019"
        referenced_author = "Friedlingstein"
        referenced_doi = "10.5194/essd-11-1783-2019"
        published_year = "2019"
    elif file_name_without_extension == 'gcb2020':
        referenced_title = "Global carbon budget 2020"
        referenced_author = "Friedlingstein"
        referenced_doi = "10.5194/essd-12-3269-2020"
        published_year = "2020"
    elif file_name_without_extension == 'Global CO2 emissions from cement production':
        referenced_title = "Global CO2 emissions from cement production"
        referenced_author = "Andrew"
        referenced_doi = "10.5194/essd-2017-77"
        published_year = "2017"
    elif file_name_without_extension == 'globalFire':
        referenced_title = "Global fire emissions estimates during 1997-2016"
        referenced_author = "Van Der Werf"
        referenced_doi = "10.5194/essd-9-697-2017"
        published_year = "2017"
    elif file_name_without_extension == 'gmb2000-2012':
        referenced_title = "The global methane budget 2000-2012"
        referenced_author = "Saunois"
        referenced_doi = "10.5194/essd-8-697-2016"
        published_year = "2016"
    elif file_name_without_extension == 'gmb2000-2017':
        referenced_title = "The global methane budget 2000-2017"
        referenced_author = "Saunois"
        referenced_doi = "10.5194/essd-12-1561-2020"
        published_year = "2020"
    else:
        return None, None, None, None
    return referenced_title, referenced_author, referenced_doi, published_year

def parse_citation(cite_json_path: str, start_id: int):
    xml_paths = []
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        keys_list = list(data.keys())

    file_name_with_extension_os = os.path.basename(cite_json_path)
    file_name_without_extension = os.path.splitext(file_name_with_extension_os)[0]
    referenced_title, referenced_author, referenced_doi, published_year = parse_target_group(file_name_without_extension)
    print(cite_json_path, referenced_title)
    
    for key_cite_title in keys_list:
        pdf_path = data[key_cite_title]
        pdf_dir, pdf_filename = os.path.split(pdf_path)
        xml_filename = os.path.splitext(pdf_filename)[0] + '.xml'
        xml_path = os.path.join(pdf_dir, xml_filename)
        bibls = getBiblStructs(xml_path)
        if(bibls==None):
            continue
        target_group = (referenced_title, referenced_author, referenced_doi)
        bibl_id = getBestMatchBiblid(target_group, bibls)
        res = []
        xml_dir, xml_filename = os.path.split(xml_path)
        citing_paper_title = key_cite_title
        if bibl_id == "None_Bibl":
            warnings.warn("no bibls, please check")
            head_title, cite_sentence = None, None
        else:
            res = matchCitationHead(xml_path, bibl_id, surname=[referenced_author], year=published_year)
            if res == None:
                head_title, cite_sentence = None, None
            else:
                for i in range(len(res)):
                    head_title = res[i][0]
                    cite_sentence = res[i][1]
                    hash_value = generate_citation_hash(citing_paper_title, referenced_title, i)
                    title_sentences.append((start_id, citing_paper_title, referenced_title, cite_sentence, head_title, ""))
                    start_id += 1
    return start_id

def list_files_in_directory(directory):
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            print(os.path.join(root, file))
            file_paths.append(os.path.join(root, file))
    return file_paths

directory = './papers'
list_files = [
    './papers/ERA5-Land.json',
    './papers/gcb2020.json',
    './papers/gmb2000-2017.json'
]
id = 0
for file_path in list_files:
    id = parse_citation(file_path, id)


import csv
# Open (or create) a CSV file with write mode ('w')
with open('result_regular_3.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    for tup in title_sentences:
        writer.writerow([tup[0], tup[1], tup[2], tup[3], tup[4], tup[5]])
pass