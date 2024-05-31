import os
import requests
from multiprocessing import Pool
import json

def send_request(pdf_path):
    url = 'http://127.0.0.2:8070/api/processFulltextDocument'

    form_data = {
        'consolidateCitations': '1',
        'segmentSentences': '1'
    }

    with open(pdf_path, 'rb') as pdf_file:
        files = {
            'input': pdf_file
        }

        try:
            # Create the XML file path
            pdf_dir, pdf_filename = os.path.split(pdf_path)
            print(pdf_filename)
            xml_filename = os.path.splitext(pdf_filename)[0] + '.xml'
            xml_path = os.path.join(pdf_dir, xml_filename)

            if not os.path.exists(xml_path):
                response = requests.post(url, data=form_data, files=files)  # Enable SSL verification
                response_text = response.text
                # Save the response as XML text with proper encoding
                with open(xml_path, 'w', encoding='utf-8') as xml_file:
                    xml_file.write(response_text)
        except requests.exceptions.RequestException as e:
            print('Error for', pdf_path, ':', e)

if __name__ == '__main__':
    # 读取json文件中的pdf存储路径并形成列表
    paths_list = []
    # 2018的已经跑过了，跳过直接跑的gmb2000-2017
    pdf_file_path = './papers/gcb2020.json'
    with open(pdf_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        paths_list = list(data.values())

    max_process_num = 6
    # List of PDF file paths

    # Create a Pool of 2 processes
    with Pool(max_process_num) as pool:
        # Send requests in parallel
        pool.map(send_request, paths_list)
