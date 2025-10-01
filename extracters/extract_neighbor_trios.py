import json
from collections import defaultdict

def load_graph_data():
    """加载图数据"""
    with open('idiom_graph.json', 'r', encoding='utf-8') as f:
        graph = json.load(f)
    return graph['nodes'], graph['edges']

def find_subgraphs_with_three_nodes(nodes, edges, min_weight=3):
    """找到所有仅包含三个节点的子图"""
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

    # 筛选大小为3的连通分量
    valid_triples = [comp for comp in components.values() if len(comp) == 3]
    
    # 提取对应的节点和边
    result = {"nodes": [], "edges": []}
    node_ids_in_triples = set()
    edge_set = set()
    
    # 收集节点信息
    node_map = {node['id']: node for node in nodes}
    for triple in valid_triples:
        for node_id in triple:
            if node_id not in node_ids_in_triples:
                node_data = node_map[node_id]
                result["nodes"].append({
                    "id": node_data["id"],
                    "explanation": node_data.get("explanation", "无解释"),
                    "similar": node_data.get("similar", []),
                    "opposite": node_data.get("opposite", [])
                })
                node_ids_in_triples.add(node_id)
    
    # 收集边信息
    for edge in edges_filtered:
        u, v = edge['source'], edge['target']
        if (u in node_ids_in_triples and v in node_ids_in_triples):
            sorted_pair = tuple(sorted([u, v]))
            if sorted_pair not in edge_set:
                result["edges"].append({
                    "source": u,
                    "target": v,
                    "weight": edge.get("weight", 0),
                    "questions": edge.get("questions", [])
                })
                edge_set.add(sorted_pair)
    
    return result

def find(parent, node):
    """路径压缩的查找"""
    if parent[node] != node:
        parent[node] = find(parent, parent[node])
    return parent[node]

def save_to_json(data, output_file='idioms_trios.json'):
    """保存结果到JSON文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"结果已保存到 {output_file}")

def main():
    # 加载数据
    nodes, edges = load_graph_data()
    
    # 提取符合条件的子图（默认过滤weight<2的边）
    result = find_subgraphs_with_three_nodes(nodes, edges, min_weight=3)
    
    # 保存结果
    save_to_json(result)

if __name__ == "__main__":
    main()