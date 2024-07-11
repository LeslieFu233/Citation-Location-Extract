from utils import *
import warnings
def add_comma_to_middle_lines(file_path):
    lines = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 处理除第一行和最后一行以外的行
    for i in range(1, len(lines) - 2):
        lines[i] = lines[i].rstrip('\n') + ',\n'

    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)