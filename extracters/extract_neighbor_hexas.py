import json
from collections import defaultdict

def load_graph_data():
    """加载图数据"""
    with open('idiom_graph.json', 'r', encoding='utf-8') as f:
        graph = json.load(f)
    return graph['nodes'], graph['edges']

def extract_medium_subgraphs(nodes, edges, min_weight=3):
    """提取节点数量大于6且小于12的子图（统一输出格式）"""
    # 并查集初始化
    parent = {}
    size = {}
    for node in nodes:
        node_id = node['id']
        parent[node_id] = node_id
        size[node_id] = 1

    # 合并操作（过滤低权重边）
    edges_filtered = [
        e for e in edges 
        if e.get('weight', 0) >= min_weight 
        and e['source'] != e['target']
    ]
    for edge in edges_filtered:
        u, v = edge['source'], edge['target']
        root_u = find(parent, u)
        root_v = find(parent, v)
        if root_u != root_v:
            if size[root_u] < size[root_v]:
                root_u, root_v = root_v, root_u
            parent[root_v] = root_u
            size[root_u] += size[root_v]

    # 统计连通分量
    components = defaultdict(list)
    for node in nodes:
        node_id = node['id']
        root = find(parent, node_id)
        components[root].append(node_id)

    # 筛选6 < 节点数 < 40的连通分量
    medium_subgraphs = [
        comp for comp in components.values() 
        if 5 < len(comp) < 11
    ]
    
    # 合并所有节点和边
    unified_data = {
        "nodes": [],
        "edges": []
    }
    node_set = set()
    edge_set = set()
    
    # 收集节点信息（去重）
    node_map = {node['id']: node for node in nodes}
    for subgraph in medium_subgraphs:
        for node_id in subgraph:
            if node_id not in node_set:
                node_data = node_map[node_id]
                unified_data["nodes"].append({
                    "id": node_data["id"],
                    "explanation": node_data.get("explanation", "无解释"),
                    "similar": node_data.get("similar", []),
                    "opposite": node_data.get("opposite", [])
                })
                node_set.add(node_id)
    
    # 收集边信息（去重）
    for edge in edges_filtered:
        u, v = edge['source'], edge['target']
        if u in node_set and v in node_set:
            sorted_pair = tuple(sorted([u, v]))
            if sorted_pair not in edge_set:
                unified_data["edges"].append({
                    "source": u,
                    "target": v,
                    "weight": edge.get("weight", 0),
                    "questions": edge.get("questions", [])
                })
                edge_set.add(sorted_pair)
    
    return unified_data

def find(parent, node):
    """路径压缩的查找"""
    if parent[node] != node:
        parent[node] = find(parent, parent[node])
    return parent[node]

def save_to_json(data, output_file='idioms_hexas.json'):
    """保存为统一格式的JSON文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"合并后的子图数据已保存到 {output_file}")

def main():
    # 加载数据
    nodes, edges = load_graph_data()
    
    # 提取符合条件的子图
    unified_data = extract_medium_subgraphs(nodes, edges)
    
    # 保存结果
    if unified_data["nodes"]:
        save_to_json(unified_data)
        print(f"共找到 {len(unified_data['nodes'])} 个节点和 {len(unified_data['edges'])} 条边")
    else:
        print("未找到节点数量在7-11之间的子图。")

if __name__ == "__main__":
    main()