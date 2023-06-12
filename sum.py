import os
import pandas as pd

# 定义文件夹路径和文件名
folder_path = r"C:\Users\Yaoyuan Zhang\Desktop\AAT\output"
idiom_file = "idiom.xlsx"
output_file = "output.xlsx"

# 读取idiom.xlsx文件中的单词数据
idiom_df = pd.read_excel(os.path.join(folder_path, idiom_file))

# 创建空的output_df用于存储结果
output_df = pd.DataFrame(columns=["单词", "次数"])

# 遍历每个xlsx文件
for filename in os.listdir(folder_path):
    if filename.endswith(".xlsx"):
        file_path = os.path.join(folder_path, filename)

        # 跳过idiom.xlsx和output.xlsx文件
        if filename == idiom_file or filename == output_file:
            continue

        # 读取当前xlsx文件
        df = pd.read_excel(file_path)

        # 遍历每一行
        for index, row in df.iterrows():
            word = row["单词"]
            count = row["次数"]

            # 检查单词是否存在于idiom中
            if word in idiom_df.values:
                # 检查单词是否已经写入output_df中
                if word in output_df["单词"].values:
                    # 更新次数
                    output_df.loc[output_df["单词"] == word, "次数"] += count
                else:
                    # 将单词和次数写入output_df
                    output_df = output_df.append({"单词": word, "次数": count}, ignore_index=True)

# 将结果写入output.xlsx
output_df.to_excel(os.path.join(folder_path, output_file), index=False)
print("处理完成，结果已写入output.xlsx文件中。")


