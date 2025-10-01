import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import jieba
from collections import defaultdict
import re

class EightDimensionClassifier:
    def __init__(self):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.questions = {}
        
        # 8个核心维度
        self.core_dimensions = {
            "个人修养": {
                "keywords": ["初心", "信念", "理想", "品德", "修养", "品质", "道德", "情操", 
                           "心态", "意志", "坚持", "耐心", "目标", "追求", "价值", "人格"],
                "sub_themes": ["道德品质", "理想信念", "心理素质", "能力修养"]
            },
            "文学艺术": {
                "keywords": ["文化", "艺术", "文学", "作品", "创作", "审美", "意境", "风格",
                           "传统", "现代", "表达", "形式", "内涵", "精神", "价值", "传承"],
                "sub_themes": ["传统文化", "文学创作", "艺术审美", "文化传承"]
            },
            "社会民生": {
                "keywords": ["社会", "民生", "人民", "群众", "公共", "服务", "保障", "公平",
                           "正义", "和谐", "稳定", "安全", "治理", "基层", "社区", "权利"],
                "sub_themes": ["民生保障", "社会治理", "社会公平", "公共服务"]
            },
            "科学技术": {
                "keywords": ["科技", "科学", "技术", "创新", "研发", "智能", "数字", "信息",
                           "进步", "发展", "研究", "探索", "发明", "创造", "应用", "突破"],
                "sub_themes": ["科技创新", "技术应用", "科学研究", "数字智能"]
            },
            "生态环保": {
                "keywords": ["生态", "环境", "保护", "自然", "资源", "可持续", "绿色", "清洁",
                           "污染", "治理", "气候", "能源", "循环", "低碳", "美丽", "家园"],
                "sub_themes": ["环境保护", "可持续发展", "生态建设", "资源利用"]
            },
            "产业发展": {
                "keywords": ["产业", "发展", "结构", "升级", "转型", "链条", "集群", "现代化",
                           "制造业", "服务业", "农业", "工业", "企业", "市场", "竞争", "创新"],
                "sub_themes": ["产业升级", "结构调整", "创新发展", "现代化产业"]
            },
            "政治文化": {
                "keywords": ["政治", "文化", "文明", "精神", "价值", "思想", "理论", "制度",
                           "治理", "领导", "民主", "法治", "国家", "民族", "认同", "自信"],
                "sub_themes": ["政治理论", "文化建设", "价值观念", "国家治理"]
            },
            "经济政策": {
                "keywords": ["经济", "政策", "发展", "增长", "市场", "调控", "改革", "开放",
                           "体制", "机制", "金融", "投资", "消费", "供给", "稳定", "平衡"],
                "sub_themes": ["宏观经济", "政策调控", "改革开放", "市场机制"]
            }
        }
    
    def load_data(self, file_path):
        """加载数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            self.questions = json.load(f)
        print(f"成功加载 {len(self.questions)} 个问题")
    
    def extract_dimension_keywords(self, text):
        """提取维度关键词"""
        words = jieba.cut(text)
        found_keywords = []
        
        for word in words:
            for dimension, info in self.core_dimensions.items():
                if word in info['keywords'] and len(word) > 1:
                    found_keywords.append((word, dimension))
        
        return found_keywords
    
    def calculate_dimension_scores(self, text):
        """计算各维度得分"""
        scores = {dimension: 0 for dimension in self.core_dimensions}
        
        # 关键词匹配得分
        keywords = self.extract_dimension_keywords(text)
        for word, dimension in keywords:
            scores[dimension] += 1
        
        # 文本内容匹配得分
        for dimension, info in self.core_dimensions.items():
            for keyword in info['keywords']:
                if keyword in text:
                    scores[dimension] += 0.5
        
        return scores
    
    def predict_dimension(self, text, options_text=""):
        """预测问题维度"""
        combined_text = text + " " + options_text
        scores = self.calculate_dimension_scores(combined_text)
        
        # 找到得分最高的维度
        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                best_dimensions = [dim for dim, score in scores.items() if score == max_score]
                best_dimension = best_dimensions[0]  # 取第一个
                
                # 确定子主题
                sub_theme = self.predict_sub_theme(best_dimension, combined_text)
                
                return {
                    'main_dimension': best_dimension,
                    'sub_theme': sub_theme,
                    'confidence': min(max_score / 5, 1.0),  # 标准化置信度
                    'dimension_scores': scores
                }
        
        return {
            'main_dimension': '其他',
            'sub_theme': '未分类',
            'confidence': 0.0,
            'dimension_scores': scores
        }
    
    def predict_sub_theme(self, dimension, text):
        """预测子主题"""
        sub_themes = self.core_dimensions[dimension]['sub_themes']
        theme_keywords_map = {
            "个人修养": {
                "道德品质": ["品德", "道德", "品质", "修养", "情操"],
                "理想信念": ["理想", "信念", "信仰", "追求", "目标"],
                "心理素质": ["心态", "心理", "情绪", "意志", "坚持"],
                "能力修养": ["能力", "素质", "本领", "才干", "智慧"]
            },
            "文学艺术": {
                "传统文化": ["传统", "文化", "历史", "遗产", "传承"],
                "文学创作": ["文学", "创作", "作品", "表达", "风格"],
                "艺术审美": ["艺术", "审美", "意境", "形式", "内涵"],
                "文化传承": ["传承", "发展", "创新", "现代", "价值"]
            },
            "社会民生": {
                "民生保障": ["民生", "保障", "就业", "教育", "医疗"],
                "社会治理": ["治理", "管理", "服务", "公共", "基层"],
                "社会公平": ["公平", "正义", "平等", "权利", "机会"],
                "公共服务": ["服务", "公共", "群众", "人民", "需求"]
            },
            "科学技术": {
                "科技创新": ["创新", "创造", "研发", "突破", "发明"],
                "技术应用": ["技术", "应用", "使用", "实践", "效果"],
                "科学研究": ["科学", "研究", "探索", "发现", "理论"],
                "数字智能": ["数字", "智能", "信息", "网络", "数据"]
            },
            "生态环保": {
                "环境保护": ["环境", "保护", "污染", "治理", "清洁"],
                "可持续发展": ["可持续", "发展", "资源", "节约", "循环"],
                "生态建设": ["生态", "建设", "自然", "系统", "平衡"],
                "资源利用": ["资源", "利用", "能源", "开发", "节约"]
            },
            "产业发展": {
                "产业升级": ["升级", "转型", "优化", "提升", "现代化"],
                "结构调整": ["结构", "调整", "布局", "配置", "协调"],
                "创新发展": ["创新", "发展", "创造", "突破", "进步"],
                "现代化产业": ["现代", "产业", "体系", "链条", "集群"]
            },
            "政治文化": {
                "政治理论": ["政治", "理论", "思想", "主义", "原理"],
                "文化建设": ["文化", "建设", "精神", "价值", "文明"],
                "价值观念": ["价值", "观念", "理念", "信念", "追求"],
                "国家治理": ["国家", "治理", "制度", "法治", "民主"]
            },
            "经济政策": {
                "宏观经济": ["经济", "宏观", "发展", "增长", "稳定"],
                "政策调控": ["政策", "调控", "干预", "引导", "支持"],
                "改革开放": ["改革", "开放", "体制", "机制", "创新"],
                "市场机制": ["市场", "机制", "竞争", "供求", "价格"]
            }
        }
        
        scores = {theme: 0 for theme in sub_themes}
        for theme in sub_themes:
            for keyword in theme_keywords_map[dimension][theme]:
                if keyword in text:
                    scores[theme] += 1
        
        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                best_themes = [theme for theme, score in scores.items() if score == max_score]
                return best_themes[0]
        
        return sub_themes[0]  # 默认返回第一个子主题
    
    def semantic_dimension_classification(self):
        """语义维度分类"""
        embeddings, question_ids = self.get_text_embeddings()
        
        # 使用聚类辅助分类
        n_clusters = min(30, len(question_ids) // 15)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(embeddings)
        
        classification_results = {}
        
        for i, qid in enumerate(question_ids):
            data = self.questions[qid]
            text = data['text']
            options_text = ' '.join(data['options'])
            
            # 基于关键词和语义的维度预测
            dimension_prediction = self.predict_dimension(text, options_text)
            
            classification_results[qid] = {
                'main_dimension': dimension_prediction['main_dimension'],
                'sub_theme': dimension_prediction['sub_theme'],
                'confidence': dimension_prediction['confidence'],
                'cluster_id': int(clusters[i]),
                'dimension_scores': dimension_prediction['dimension_scores'],
                'keywords': list(set([kw for kw, dim in self.extract_dimension_keywords(text)]))
            }
        
        return classification_results
    
    def get_text_embeddings(self):
        """获取文本嵌入"""
        texts = []
        question_ids = []
        
        for qid, data in self.questions.items():
            text = data['text']
            options_text = ' '.join(data['options'])
            combined_text = f"{text} {options_text}"
            combined_text = self.preprocess_text(combined_text)
            
            texts.append(combined_text)
            question_ids.append(qid)
        
        print("正在生成文本嵌入...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings, question_ids
    
    def preprocess_text(self, text):
        """文本预处理"""
        text = re.sub(r'[^\u4e00-\u9fa5，。！？；：""（）《》\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def save_dimension_classification(self, output_file):
        """保存维度分类结果"""
        results = self.semantic_dimension_classification()
        
        # 按维度组织结果
        dimension_results = defaultdict(lambda: defaultdict(dict))
        
        for qid, info in results.items():
            main_dimension = info['main_dimension']
            sub_theme = info['sub_theme']
            
            dimension_results[main_dimension][sub_theme][qid] = {
                'text': self.questions[qid]['text'],
                'options': self.questions[qid]['options'],
                'analysis': self.questions[qid]['analysis'],
                'classification_info': info
            }
        
        # 保存到文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dimension_results, f, ensure_ascii=False, indent=2)
        
        self.print_dimension_statistics(dimension_results)
        
        return dimension_results
    
    def print_dimension_statistics(self, dimension_results):
        """打印维度统计"""
        print("\n🎯 8维度分类统计结果:")
        print("=" * 60)
        
        total_questions = sum(
            len(sub_questions) 
            for dimension in dimension_results.values() 
            for sub_questions in dimension.values()
        )
        
        print(f"总问题数: {total_questions}")
        print()
        
        for dimension, sub_themes in sorted(dimension_results.items()):
            dimension_count = sum(len(questions) for questions in sub_themes.values())
            dimension_percentage = (dimension_count / total_questions) * 100
            
            print(f"📊 {dimension}: {dimension_count} 题 ({dimension_percentage:.1f}%)")
            print("-" * 40)
            
            for sub_theme, questions in sorted(sub_themes.items(), key=lambda x: len(x[1]), reverse=True):
                sub_count = len(questions)
                sub_percentage = (sub_count / total_questions) * 100
                
                # 计算平均置信度
                confidences = [q['classification_info']['confidence'] for q in questions.values()]
                avg_confidence = np.mean(confidences) if confidences else 0
                
                print(f"  📍 {sub_theme}: {sub_count} 题 ({sub_percentage:.1f}%)")
                print(f"     平均置信度: {avg_confidence:.3f}")
                
                # 显示代表性题目
                sample_qids = list(questions.keys())[:2]
                for sample_qid in sample_qids:
                    sample_text = questions[sample_qid]['text'][:60] + "..."
                    confidence = questions[sample_qid]['classification_info']['confidence']
                    print(f"     • 问题{sample_qid}[{confidence:.3f}]: {sample_text}")
            
            print()
    
    def analyze_dimension_distribution(self):
        """分析维度分布"""
        results = self.semantic_dimension_classification()
        
        dimension_counts = defaultdict(int)
        confidence_by_dimension = defaultdict(list)
        
        for qid, info in results.items():
            dimension = info['main_dimension']
            dimension_counts[dimension] += 1
            confidence_by_dimension[dimension].append(info['confidence'])
        
        print("\n📈 维度分布分析:")
        print("=" * 50)
        
        total = sum(dimension_counts.values())
        for dimension, count in sorted(dimension_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            avg_confidence = np.mean(confidence_by_dimension[dimension]) if confidence_by_dimension[dimension] else 0
            print(f"{dimension}: {count} 题 ({percentage:.1f}%) - 平均置信度: {avg_confidence:.3f}")

# 使用示例
def main():
    classifier = EightDimensionClassifier()
    classifier.load_data('merged_questions.json')
    
    print("开始8维度分类...")
    results = classifier.save_dimension_classification('8dimension_classified.json')
    
    print("\n📊 维度分布分析...")
    classifier.analyze_dimension_distribution()
    
    print("✅ 8维度分类完成！")

if __name__ == "__main__":
    main()
