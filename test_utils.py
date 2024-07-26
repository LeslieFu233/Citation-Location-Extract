# from utils import *
# import os
# xml_path = "citelabel.xml"
# s = matchCitationHead(xml_path, "b35", surname=["Munoz-Sabater"], year="2021")
# for s_i in s:
#     print(s_i[1] + "\n\n")

import numpy as np
import pandas as pd
from simhash import Simhash
from utils import *

class Citation:
    def __init__(self, citing_title, referenced_title, citing_sentence):
        self.citing_title = citing_title
        self.referenced_title = referenced_title
        self.citing_sentence = citing_sentence
        self.hash = Simhash(f"{citing_title}-{referenced_title}-{citing_sentence}")


def read_csv_and_generate_citations(csv_path):
    df = pd.read_csv(csv_path, usecols=[1, 2, 3])
    citations = [Citation(row.iloc[0], row.iloc[1], extract_sentence_with_citation(row.iloc[2])) for index, row in df.iterrows()]
    return citations, df

def get_hash_distance(hash1, citations2):
    return np.array([hash1.distance(citation.hash) for citation in citations2])

def build_similarity_matrix(citations1, citations2):
    total_results = []
    for citation1 in citations1:
        distances = get_hash_distance(citation1.hash, citations2)
        total_results.append(distances)
    similarity_matrix = np.array(total_results)
    return similarity_matrix

def remove_dot_before_citation(text):
    pattern = re.compile(r'\.\s*######citaion#####')
    result = pattern.sub(' ######citaion#####', text)
    return result

# # 读取CSV文件并生成Citation对象
# df = pd.read_csv('result_regular_edit.csv', header=None, encoding_errors='replace')

# # 生成hash值并替换第一列
# # 假设列的索引从0开始，第2，3，4列的索引分别为1，2，3
# df.iloc[:, 0] = df.apply(lambda row: generate_citation_hash(str(row.iloc[1]), str(row.iloc[2]), extract_sentence_with_citation(remove_dot_before_citation(str(row.iloc[3])))).value, axis=1)

# # 保存修改后的DataFrame到CSV
# df.to_csv('modified_file.csv', index=False)

# # 构建相似度矩阵并找到最相似的项
# similarity_matrix = build_similarity_matrix(citations_file1, citations_file2)
# min_indices = np.argmin(similarity_matrix, axis=1)
# mapping = {citations_file1[row_index]: citations_file2[min_index] for row_index, min_index in enumerate(min_indices)}

# # 输出或处理Citation对象之间的映射关系
# for first, second in mapping.items():
#     print(f"{first.citing_title} -> {second.citing_title}")

import csv
from simhash import Simhash
import numpy as np

def read_hashes(csv_path):
    hashes = []
    with open(csv_path, 'r', encoding='utf-8', errors="replace") as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # 跳过标题行
        for row in reader:
            if row:
                try:
                    # 尝试将第一列的值转换为整数
                    hash_value = int(row[0])
                    # 如果转换成功，创建Simhash对象
                    hashes.append(Simhash(hash_value))
                except ValueError:
                    # 如果转换失败，打印错误信息并跳过该行
                    print(f"Skipping row with invalid integer value: {row[0]}")
    return hashes

def calculate_similarity_matrix(hashes1, hashes2, csv1, csv2):
    matrix = np.zeros((len(hashes1), len(hashes2)))

    # 使用csv模块加载CSV文件的第二列和第三列
    def load_titles(csv_path):
        titles = []
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # 跳过标题行
            for row in reader:
                titles.append((row[1], row[2]))  # 只读取第二列和第三列
        return titles

    titles1 = load_titles(csv1)
    titles2 = load_titles(csv2)

    for i, hash1 in enumerate(hashes1):
        for j, hash2 in enumerate(hashes2):
            # 检查第二列和第三列的值是否相同
            if titles1[i][0] == titles2[j][0]:
                # 计算汉明距离，并转换为相似度
                distance = hash1.distance(hash2)
                similarity = 64 - distance  # 假设哈希值是64位的
                matrix[i, j] = similarity
            else:
                # 如果不相同，相似度设为0
                matrix[i, j] = 0
    return matrix

def find_best_matches(similarity_matrix):
    return np.argmax(similarity_matrix, axis=1)

def write_mapping_to_csv(mapping, output_path):
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['CSV1 Row Index', 'CSV2 Best Match Row Index'])
        for i, match in enumerate(mapping):
            writer.writerow([i, match])

# 主逻辑
csv_path1 = 'result_regular_test.csv'
csv_path2 = 'modified_file.csv'
output_path = 'mapping.csv'

hashes1 = read_hashes(csv_path1)
hashes2 = read_hashes(csv_path2)
similarity_matrix = calculate_similarity_matrix(hashes1, hashes2, csv_path1, csv_path2)
mapping = find_best_matches(similarity_matrix)
write_mapping_to_csv(mapping, output_path)
