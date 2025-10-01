import json
import re

def replace_spaces_with_underscores(input_file, output_file):
    """
    将questions.bank.json文件中text字段的连续空格替换为下划线
    
    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
    """
    try:
        # 读取JSON文件
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 统计替换数量
        replace_count = 0
        
        # 遍历每个问题
        for question_id, question_data in data.items():
            if 'text' in question_data:
                original_text = question_data['text']
                # 将连续的空格（至少4个）替换为下划线
                # 可以根据需要调整空格数量
                new_text = re.sub(r' {4,}', '_____', original_text)
                
                # 如果文本被修改，更新数据并计数
                if new_text != original_text:
                    question_data['text'] = new_text
                    replace_count += 1
                    print(f"问题 {question_id}: 已替换空格")
        
        # 保存修改后的数据
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"\n处理完成！")
        print(f"共处理 {len(data)} 个问题")
        print(f"替换了 {replace_count} 个问题中的空格")
        print(f"输出文件: {output_file}")
        
    except FileNotFoundError:
        print(f"错误: 找不到文件 {input_file}")
    except json.JSONDecodeError:
        print(f"错误: {input_file} 不是有效的JSON格式")
    except Exception as e:
        print(f"发生错误: {e}")

# 使用示例
if __name__ == "__main__":
    input_file = "merged_questions.json"  # 输入文件路径
    output_file = "qustions_bank.json"  # 输出文件路径
    
    replace_spaces_with_underscores(input_file, output_file)
