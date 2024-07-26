from utils import *
import warnings
import os
import json
import pandas as pd

title_sentences = []

def parse_target_group(file_name_without_extension):
    """Parse the target group of the citation.

    Args:
        file_name_without_extension (str): The name of the file without the extension.

    Returns:
        tuple: A tuple containing the referenced title, author, DOI, and published year.
               If the file name is not recognized, all values in the tuple will be None.
    """
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
    """
    Parses citation information from a JSON file and extracts relevant data.
    This JSON file's every item is a paper title(key) and the path of tei-xml file(value).

    Such as:
    {
        "paper_title": "tei-xml file path",
        "paper_title2": "tei-xml file path2",
        ...
    }
    Please make sure your JSON format is correct.

    Args:
        cite_json_path (str): The path to the JSON file containing citation data.
        start_id (int): The starting ID for the citation.

    Returns:
        int: The updated starting ID for the citation.
    """
    xml_paths = []
    with open(cite_json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        # data.keys() returns all titles of the papers
        keys_list = list(data.keys())

    file_name_with_extension_os = os.path.basename(cite_json_path)
    file_name_without_extension = os.path.splitext(file_name_with_extension_os)[0]
    referenced_title, referenced_author, referenced_doi, published_year = parse_target_group(file_name_without_extension)
    print(cite_json_path, referenced_title)
    
    for key_cite_title in keys_list:
        # data[key] means tei file path
        pdf_path = data[key_cite_title]
        pdf_dir, pdf_filename = os.path.split(pdf_path)
        xml_filename = os.path.splitext(pdf_filename)[0] + '.xml'
        xml_path = os.path.join(pdf_dir, xml_filename)
        bibls = getBiblStructs(xml_path)
        if(bibls==None):
            continue
        target_group = (referenced_title, referenced_author, referenced_doi)
        #Finds the best matching bibl ID based on the target group and match weights.
        bibl_id = getBestMatchBiblid(target_group, bibls)
        res = []
        xml_dir, xml_filename = os.path.split(xml_path)
        citing_paper_title = clean_html(key_cite_title)
        if bibl_id == "None_Bibl":
            warnings.warn("no bibls, please check")
            head_title, cite_para = None, None
        else:
            match_items, abstract_context, keywords_context = matchCitationHead(xml_path, bibl_id, surname=[referenced_author], year=published_year)
            if match_items == None:
                head_title, cite_para = None, None
            else:
                abstract_text = abstract_context[0]
                abstract_word_count = abstract_context[1]
                keywords_text = keywords_context[0]
                keywords_count = keywords_context[1]
                for i in range(len(match_items)):
                    head_title = match_items[i][0]
                    citation_context = match_items[i][1]
                    cite_para = citation_context[0]
                    cite_sentence_word_count = citation_context[1]
                    citing_sentence = citation_context[2]
                    hash_value = generate_citation_hash(citing_paper_title, referenced_title, citing_sentence)
                    hash_hex_value = f"{hash_value.value:016x}"
                    title_sentences.append((hash_hex_value, citing_paper_title, referenced_title, cite_para, cite_sentence_word_count, head_title, abstract_text))

def list_files_in_directory(directory):
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            print(os.path.join(root, file))
            file_paths.append(os.path.join(root, file))
    return file_paths

# example
directory = './papers'
list_files = list_files_in_directory(directory)
for file in list_files:
    parse_citation(file, 0)
import csv
headers = ["Citation ID", "Citing Paper Title", "Data Paper Title", "Citation Content", "Citation Sentence Word Count", "Head Title", "Abstract Text"]
# Open (or create) a CSV file with write mode ('w')
with open('result_regular_test_hash.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    for tup in title_sentences:
        writer.writerow([tup[i] for i in range(len(tup))])
pass

#直接生成xlsx文件
# 将元组列表转换为 DataFrame
#df = pd.DataFrame(title_sentences, columns=headers)

# 将 DataFrame 写入 Excel 文件
#df.to_excel("output.xlsx", index=False)