import pandas as pd

# 定义文件路径和文件名
idiom_file = "idioms.xlsx"
output_file = "output.xlsx"

# 读取idioms.xlsx文件
idiom_df = pd.read_excel(idiom_file)

# 读取output.xlsx文件
output_df = pd.read_excel(output_file)

# 添加"意思"和"拼音"列
output_df["意思"] = ""
output_df["拼音"] = ""

# 遍历output.xlsx中的单词列
for index, row in output_df.iterrows():
    word = row["单词"]

    # 检查单词是否存在于idioms.xlsx的"word"列中
    if word in idiom_df["word"].values:
        # 获取匹配单词的行
        match_row = idiom_df[idiom_df["word"] == word].iloc[0]

        # 复制"explanation"和"pinyin"的内容到"意思"和"拼音"列中
        output_df.at[index, "意思"] = match_row["explanation"]
        output_df.at[index, "拼音"] = match_row["pinyin"]

# 将结果写回output.xlsx文件
output_df.to_excel(output_file, index=False)
print("处理完成，结果已写入output.xlsx文件中。")
