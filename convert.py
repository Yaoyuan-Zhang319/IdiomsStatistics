import pandas as pd
import json

# 读取JSON文件
with open('idiom.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 创建一个DataFrame对象
df = pd.DataFrame(data)

# 指定列的顺序
columns = ["derivation", "example", "explanation", "pinyin", "word", "abbreviation"]
df = df[columns]

# 将DataFrame保存为Excel文件
df.to_excel('idioms.xlsx', index=False)
