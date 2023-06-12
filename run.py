import os
from PyPDF2 import PdfReader

# 指定PDF文件所在的文件夹路径
pdf_folder = "C:/Users/Yaoyuan Zhang/Desktop/AAT/folder/"

# 指定TXT文件保存的路径
txt_file = "library.txt"

# 定义部分名称
section_names = ["常识判断", "言语理解", "数量关系", "判断推理", "资料分析"]

# 定义目标部分
target_section = "言语理解"

# 遍历文件夹中的每个PDF文件
for filename in os.listdir(pdf_folder):
    if filename.endswith(".pdf"):
        # 构建PDF文件的完整路径
        pdf_path = os.path.join(pdf_folder, filename)

        # 打开PDF文件
        with open(pdf_path, "rb") as pdf_file:
            # 创建一个PDF阅读器对象
            reader = PdfReader(pdf_file)

            # 初始化标志变量
            found_target_section = False

            # 遍历PDF的每一页
            for page in reader.pages:
                # 获取当前页的内容
                text = page.extract_text()

                # 检查每个部分是否出现
                for section_name in section_names:
                    # 检查目标部分是否出现
                    if section_name == target_section and section_name in text:
                        found_target_section = True
                        break

                    # 检查其他部分是否出现
                    if section_name != target_section and section_name in text:
                        found_target_section = False
                        break

                # 写入TXT文件
                if found_target_section:
                    with open(txt_file, "a", encoding="utf-8") as txt:
                        txt.write(text)

        print(f"提取完成：{pdf_path}")

print(f"所有PDF文件中的'{target_section}'部分已写入到library.txt文件中。")





