import os
import requests
from multiprocessing import Pool
import json

def send_request(pdf_path, url_base='http://127.0.0.2:8070/'):
    """
    Sends a request to the Grobid server to process a PDF file and save the response as an XML file.

    When you use it, you should deploy the Grobid server first. Please follow the instructions by visiting the link below:
    https://grobid.readthedocs.io/en/latest.

    And if you want to use your own request method, you can refer to the link below:
    https://grobid.readthedocs.io/en/latest/Grobid-service/#grobid-web-services

    Args:
        pdf_path (str): The path to the PDF file to be processed.
        url_base (str, optional): The base URL of the Grobid server. Defaults to 'http://127.0.0.2:8070/'.

    Raises:
        requests.exceptions.RequestException: If there is an error in sending the request.

    Returns:
        None
    """
    url = url_base + 'api/processFulltextDocument'
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

# This is a example of how to use send pdf2xml request to grobid server in parallel
if __name__ == '__main__':
    # read the pdf file paths from json file
    paths_list = []
    pdf_file_path = './papers/gcb2020.json'
    with open(pdf_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        paths_list = list(data.values())

    #Process num 
    max_process_num = 6

    with Pool(max_process_num) as pool:
        # Send requests in parallel
        pool.map(send_request, paths_list)
