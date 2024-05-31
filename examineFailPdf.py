import os
import PyPDF2

# 定义一个函数来检查PDF文件是否能够成功打开
def is_valid_pdf(file_path):
    try:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfFileReader(pdf_file)
            if pdf_reader.getNumPages() > 0:
                return True
            else:
                return False
    except Exception as e:
        return False

# 指定要检测的文件夹路径
folder_path = './（二刷）Global fire emissions estimates during 1997-2016/（二刷）Global fire emissions estimates during 1997-2016'

# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    if filename.lower().endswith('.pdf') and not is_valid_pdf(file_path):
        print(f"Invalid PDF: {filename}")

