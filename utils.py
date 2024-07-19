import xml.etree.ElementTree as ET
from MatchObject import SimilarityMeasure, BinaryMeasure
from collections import OrderedDict
import re
import hashlib
import PyPDF2
import string
import nltk
nltk.download('punkt')

def is_valid_pdf(file_path):
    """
    Checks if a PDF file is valid by attempting to open it and checking if it has at least one page.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        bool: True if the PDF file is valid, False otherwise.
    """
    try:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfFileReader(pdf_file)
            if pdf_reader.getNumPages() > 0:
                return True
            else:
                return False
    except Exception as e:
        return False

def add_comma_to_middle_lines(file_path):
    """
    Adds a comma to the end of each line, except for the first and last line, in a given file.

    Args:
        file_path (str): The path to the file.
    """
    lines = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Process lines except for the first and last line
    for i in range(1, len(lines) - 2):
        lines[i] = lines[i].rstrip('\n') + ',\n'

    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)

def word_count(text:str):
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'(\b[A-Za-z]+)\s+(\d+\b)', r'\1\2', text)
    words = nltk.tokenize.word_tokenize(text.lower())
    words = [word for word in words if word.isalnum()]
    return len(words)

def get_text_excluding_refs(element):
    text = ''
    if element.tag != 'ref':
        if element.text:
            text += element.text
    for child in element:  # 递归处理子元素
        text += get_text_excluding_refs(child)
        if child.tail:
            text += child.tail
    return text

def get_key_words(element:ET.Element, namespace="{http://www.tei-c.org/ns/1.0}") -> list:
    """
    Extracts the key words from a TEI XML element.

    Args:
        element (ET.Element): The TEI XML element to extract key words from.
        namespace (str, optional): The namespace used in the TEI XML element. Defaults to "{http://www.tei-c.org/ns/1.0}".

    Returns:
        list: A list of key words extracted from the element.
    """
    key_words = []
    for keyword in element.iter(namespace + 'term'):
        key_words.append(keyword.text)
    return key_words

def extract_first_number(str):
    """Extract the first number from a string."""
    match = re.search(r'\d+', str)
    return int(match.group(0)) if match else None

def get_related_sentence(index, sentences=[]):
    """
    Returns a string containing the sentences from the given list, with the sentence at the specified index marked with "######citaion#####".

    Parameters:
    index (int): The index of the sentence to mark as a citation.
    sentences (list): The list of sentences to process.

    Returns:
    str: A string containing the sentences, with the citation marked.
    """
    related_sentence = ""
    citing_sentence_word_count = 0
    for i in range(len(sentences)):
        if sentences[i].text == None:
            continue
        if i == index:
            citing_sentence = get_text_excluding_refs(sentences[i])
            related_sentence +=  citing_sentence + " ######citaion##### "
            citing_sentence_word_count = word_count(citing_sentence)
        else:
            related_sentence += get_text_excluding_refs(sentences[i])
    return related_sentence, citing_sentence_word_count

def getBiblStructs(tei_path, namespace = "{http://www.tei-c.org/ns/1.0}"):
    """
    Retrieves the bibliographic structures from a TEI XML file.

    Args:
        tei_path (str): The path to the TEI XML file.
        namespace (str, optional): The namespace used in the TEI XML file. Defaults to "{http://www.tei-c.org/ns/1.0}".

    Returns:
        Element: The bibliographic structures as an Element object, or None if not found.
    """
    try:
        tree = ET.parse(tei_path)
    except ET.ParseError as e:
        print(f"XML parsing error: {e}, xml_path:{tei_path}")
        return None
    back = None
    for i in tree.iter():
        if 'back' in i.tag:
            back = i
            break
    if back==None:
        return None
    bibls = back.find('./' + namespace + 'div[@type="references"]')
    bibls = bibls.find(namespace + 'listBibl')
    return bibls

def matchCitationHead(tei_path, bibl_id, namespace="{http://www.tei-c.org/ns/1.0}", surname=None, year=None):
    """
    Matches the citation head in a TEI XML file based on the given parameters.

    Args:
        tei_path (str): The path to the TEI XML file.
        bibl_id (str): The ID of the citation to match.
        namespace (str, optional): The namespace of the TEI XML file. Defaults to "{http://www.tei-c.org/ns/1.0}".
        surname (list, optional): A list of surnames to match in the citation text. Defaults to None.
        year (str, optional): The year to match in the citation text. Defaults to None.

    Returns:
        TODO: should add a description about the return list
        list: A list of matched citation items, each containing the section title and the related sentence.

    """
    tree = ET.parse(tei_path)
    keywords = None
    body = None
    abstract = None 
    keywords_list = []
    matched_items = []
    # get abstract and body from tei tree
    for i in tree.iter():
        if 'keywords' in i.tag:
            keywords = i
        if 'abstract' in i.tag:
            abstract = i
        if 'body' in i.tag:
            body = i
            break
    if keywords != None:
        keywords_list = get_key_words(keywords)
    abstract_title = abstract.find(namespace + 'div')
    if abstract_title != None:
        sentences = abstract_title.findall('.//' + namespace + 's')
        # match bibl_id in abstract's every sentence
        for s_index, sentence in enumerate(sentences):
            refs = sentence.findall('.//' + namespace + 'ref[@type="bibr"]')
            for ref in refs:
                match_bibl_id =  ref.attrib.get('target')
                ref_text = ref.text
                if match_bibl_id == '#' + bibl_id:
                    matched_items.append(('Introduction', get_related_sentence(s_index, sentences)))
                elif ref_text!=None and (year!=None and year in ref_text) and any(s.lower() in ref_text.lower() for s in surname):
                    matched_items.append(('Introduction', get_related_sentence(s_index, sentences)))

    paras = body.findall(namespace + 'div')
    head_title_dic = OrderedDict()
    for index, para in enumerate(paras):
        # get head title and sentences from every para
        head_title = para.find(namespace + 'head')
        if(head_title != None):
            head_level = get_head_level(head_title)
            head_title = head_title.text
            head_title_dic[head_title] = head_level
        sentences = para.findall('.//' + namespace + 's')
        for s_index, sentence in enumerate(sentences):
            # find all references in the sentence
            refs = sentence.findall('.//' + namespace + 'ref[@type="bibr"]')
            for ref in refs:
                match_bibl_id =  ref.attrib.get('target')
                ref_text = ref.text
                if match_bibl_id == '#' + bibl_id:
                    if head_title!=None:
                        matched_items.append((get_parent_head(head_title_dic, head_title), get_related_sentence(s_index, sentences)))
                    else:
                        if(index == 0):    matched_items.append(('Introduction', get_related_sentence(s_index, sentences)))
                        else:   matched_items.append(('NoTitle', get_related_sentence(s_index, sentences)))
                elif ref_text!=None and (year!=None and year in ref_text) and any(s.lower() in ref_text.lower() for s in surname):
                    matched_items.append((get_parent_head(head_title_dic, head_title), get_related_sentence(s_index, sentences)))
                
                elif ref_text!=None and extract_first_number(ref_text)==extract_first_number(bibl_id) + 1:
                    matched_items.append((get_parent_head(head_title_dic, head_title), get_related_sentence(s_index, sentences)))
    return matched_items

def getMatch(biblStruct:ET.Element, namespace = "{http://www.tei-c.org/ns/1.0}"):
    """
    Extracts information from a TEI XML element representing a bibliographic structure.

    Args:
        biblStruct (ET.Element): The TEI XML element representing the bibliographic structure.
        namespace (str, optional): The namespace used in the TEI XML element. Defaults to "{http://www.tei-c.org/ns/1.0}".

    Returns:
        tuple: A tuple containing the extracted information in the following order: 
               - title_text (str): The main title of the bibliographic structure.
               - first_author_surname (str): The surname of the first author.
               - doi_no (str): The DOI number of the bibliographic structure.

    """
    analytic = biblStruct.find(namespace + 'analytic')
    title_text = None
    first_author_surname = None
    doi_no = None

    if(analytic == None):
        return None
    
    title = analytic.find('./' + namespace + 'title[@type="main"]')
    if title !=None:
        title_text = title.text
    
    author = analytic.find(namespace + 'author')
    if author!=None:
        first_author_persName = author.find(namespace + 'persName')
        if first_author_persName !=None:
            first_author_surname = first_author_persName.find(namespace + 'surname')
            if first_author_surname != None: first_author_surname = first_author_surname.text

    doi = analytic.find('./' + namespace + 'idno[@type="DOI"]')
    if doi!=None:
        doi_no = doi.text

    return (title_text, first_author_surname, doi_no)

def getMatchScore(target_group:tuple, match_group:tuple, match_weights:tuple):
    """Calculate the match score between target_group and match_group based on match_weights.
       Please refer to MatchObject.py to see the definition of SimilarityMeasure and BinaryMeasure.

    Args:
        target_group (tuple): A tuple representing the target group.
        match_group (tuple): A tuple representing the match group.
        match_weights (tuple): A tuple representing the match weights.

    Returns:
        float: The match score between target_group and match_group. Higher scores indicate better matches.
    """
    if match_group == None: return 0
    assert len(target_group) == len(match_group) == len(match_weights), "Tuples' length presents match types' amount. "
    match_score = 0
    for i in range(len(target_group)):
        match_method = None
        if match_weights[i][2] == "similarity":
            match_method = SimilarityMeasure()
        elif match_weights[i][2] == "binary":
            match_method = BinaryMeasure()
        if match_method != None and match_group[i] != None and target_group[i] != None:
            similarity = match_method.calculate_similarity(target_group[i], match_group[i])
            match_score += match_weights[i][1] * similarity
        
    return match_score

def getBestMatchBiblid(
    target_group, 
    bibls:ET.Element,
    namespace = "{http://www.tei-c.org/ns/1.0}", 
    match_weights = [('title', 0.8, "similarity"),('surname', 0.1, "similarity"),('doi', 0.1, "binary")]):
    """
    Finds the best matching bibl ID based on the target group and match weights.

    Parameters:
    - target_group: The target group to match against.
    - bibls: The XML element containing the biblStruct elements.
    - namespace: The namespace of the XML elements (default: "{http://www.tei-c.org/ns/1.0}").
    - match_weights: A list of tuples specifying the match weights for different attributes (default: [('title', 0.8, "similarity"),('surname', 0.1, "similarity"),('doi', 0.1, "binary")]).

    Returns:
    - The best matching bibl ID.

    If no match is found, it returns "None_Bibl".
    """
    match_scores = []
    for bibl in bibls.iter(namespace + 'biblStruct'):
        bibl_id = next(iter(bibl.attrib.values()))
        match_group = getMatch(bibl)
        match_score = getMatchScore(target_group, match_group, match_weights)
        match_scores.append((bibl_id, match_score))
    if(len(match_scores)==0):
        return "None_Bibl"
    max_bibl_id = max(match_scores, key=lambda x: x[1])[0]
    return max_bibl_id

def get_head_level(head_title:ET.Element, init_head_level=0):
    """
    Get the level of a head title element.

    Parameters:
    - head_title (ET.Element): The head title element.
    - init_head_level (int): The initial head level.

    Returns:
    - int: The level of the head title element.
    """
    head_level = head_title.attrib.get('n')
    if head_level == None:
        return init_head_level
    head_level = head_level.split('.')
    head_level = len(list(filter(lambda s: s != "", head_level)))
    return head_level

from collections import OrderedDict

def get_parent_head(head_title_dic: OrderedDict, head_title, init_head_level=0):
    """
    Returns the parent head title based on the given head title dictionary and target head title.

    Parameters:
    head_title_dic (OrderedDict): The dictionary containing the head titles and their levels.
    head_title (str): The target head title.
    init_head_level (int): The initial head level.

    Returns:
    str: The parent head title.

    """
    target_level = 1
    find_flag = False
    for title, level in reversed(head_title_dic.items()):
        if find_flag:
            if level == target_level:
                return title
            else:
                continue
        elif title == head_title:
            if level == 0 or level == target_level:
                return title
            find_flag = True

import hashlib

def generate_citation_hash(citing_title, referenced_title, citing_index):
    """
    Generate a hash value for a citation based on the citing title, referenced title, and citing index.

    Args:
        citing_title (str): The title of the citing document.
        referenced_title (str): The title of the referenced document.
        citing_index (int): The index of the citation.

    Returns:
        str: The hash value generated for the citation.
    """
    unique_string = f"{citing_title}-{referenced_title}-{citing_index}"

    hash_object = hashlib.sha256(unique_string.encode())
    hash_hex = hash_object.hexdigest()
    
    return hash_hex

