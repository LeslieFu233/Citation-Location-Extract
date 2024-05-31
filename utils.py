import xml.etree.ElementTree as ET
from MatchObject import SimilarityMeasure, BinaryMeasure
from collections import OrderedDict
import re
import hashlib
def extract_first_number(str):
    match = re.search(r'\d+', str)
    return int(match.group(0)) if match else None

def get_related_sentence(index, sentences=[]):
    related_sentence = ""
    for i in range(len(sentences)):
        if(sentences[i].text == None): continue
        if i == index:
            related_sentence += sentences[i].text + " ######citaion##### "
        else:
            related_sentence += sentences[i].text
    return related_sentence

def getBiblStructs(tei_path, namespace = "{http://www.tei-c.org/ns/1.0}"):
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

def matchCitationHead(tei_path, bibl_id, namespace = "{http://www.tei-c.org/ns/1.0}", surname=None, year=None):
    tree = ET.parse(tei_path)
    body = None
    abstract = None 
    matched_items = []
    for i in tree.iter():
        if 'abstract' in i.tag:
            abstract = i
        if 'body' in i.tag:
            body = i
            break
    abstract_title = abstract.find(namespace + 'div')
    if abstract_title != None:
        sentences = abstract_title.findall('.//' + namespace + 's')
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
        head_title = para.find(namespace + 'head')
        if(head_title != None):
            head_level = get_head_level(head_title)
            head_title = head_title.text
            head_title_dic[head_title] = head_level
        sentences = para.findall('.//' + namespace + 's')
        for s_index, sentence in enumerate(sentences):
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
    """如果以后需要修改或者新增相似度度量模式，就在这里改，否则，新增要匹配的项统统在调用的地方修改

    Args:
        target_group (tuple): _description_
        match_group (tuple): _description_
        match_weights (tuple): _description_

    Returns:
        _type_: _description_
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
    head_level = head_title.attrib.get('n')
    if head_level == None:
        return init_head_level
    head_level = head_level.split('.')
    head_level = len(list(filter(lambda s: s != "", head_level)))
    return head_level
def get_parent_head(head_title_dic:OrderedDict, head_title, init_head_level=0):
    target_level = 1
    find_flag = False
    for title, level in reversed(head_title_dic.items()):
        if find_flag:
            if level == target_level: return title
            else: continue
        elif title == head_title:
            if level == 0 or level == target_level: return title
            find_flag = True
# xml_path='D:\\CSTCloud\\programs\\references\\storage\\KFPULJ3T\\Kurganova 等 - 2023 - Temperature Sensitivity of Soil Respiration in Gra.xml'
# bibls = getBiblStructs(xml_path)

#     # target_group = ('Global carbon budget 2016', 'Quéré', '10.5194/essd-8-605-2016')
# target_group = ('Global carbon budget 2019', 'Friedlingstein', '10.5194/essd-11-1783-2019')
# bibl_id = getBestMatchBiblid(target_group, bibls)

# if bibl_id == "None_Bibl":
#     warnings.warn("no bibls, please check")

# head_title = matchCitationHead(xml_path, bibl_id, surname='Friedlingstein', year='2019')
# print(bibl_id, head_title)

def generate_citation_hash(citing_title, referenced_title, citing_index):

    unique_string = f"{citing_title}-{referenced_title}-{citing_index}"

    hash_object = hashlib.sha256(unique_string.encode())
    hash_hex = hash_object.hexdigest()
    
    return hash_hex
