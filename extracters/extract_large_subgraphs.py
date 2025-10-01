import json
from collections import defaultdict

def load_graph_data():
    """加载图数据"""
    with open('idiom_graph.json', 'r', encoding='utf-8') as f:
        graph = json.load(f)
    return graph['nodes'], graph['edges']

def extract_large_subgraphs(nodes, edges, min_weight=3, min_size=10):
    """提取所有节点数量大于 min_size 的子图，并保存为 JSON 文件"""
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

    # 筛选大小 > min_size 的连通分量
    large_subgraphs = [comp for comp in components.values() if len(comp) > min_size]
    
    # 提取对应的节点和边
    result = []
    for subgraph in large_subgraphs:
        subgraph_data = {"nodes": [], "edges": []}
        node_ids_in_subgraph = set(subgraph)
        
        # 收集节点信息
        node_map = {node['id']: node for node in nodes}
        for node_id in subgraph:
            node_data = node_map[node_id]
            subgraph_data["nodes"].append({
                "id": node_data["id"],
                "explanation": node_data.get("explanation", "无解释"),
                "similar": node_data.get("similar", []),
                "opposite": node_data.get("opposite", [])
            })
        
        # 收集边信息
        edge_set = set()
        for edge in edges_filtered:
            u, v = edge['source'], edge['target']
            if u in node_ids_in_subgraph and v in node_ids_in_subgraph:
                sorted_pair = tuple(sorted([u, v]))
                if sorted_pair not in edge_set:
                    subgraph_data["edges"].append({
                        "source": u,
                        "target": v,
                        "weight": edge.get("weight", 0),
                        "questions": edge.get("questions", [])
                    })
                    edge_set.add(sorted_pair)
        
        result.append(subgraph_data)
    
    return result

def find(parent, node):
    """路径压缩的查找"""
    if parent[node] != node:
        parent[node] = find(parent, parent[node])
    return parent[node]

def save_to_json(subgraphs, output_prefix='large_subgraph_'):
    """将每个子图保存为单独的 JSON 文件"""
    for i, subgraph in enumerate(subgraphs, 1):
        output_file = f"{output_prefix}{i}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(subgraph, f, ensure_ascii=False, indent=2)
        print(f"子图 {i} 已保存到 {output_file}")

def main():
    # 加载数据
    nodes, edges = load_graph_data()
    
    # 提取节点数量 > 35 的子图
    large_subgraphs = extract_large_subgraphs(nodes, edges, min_size=10)
    
    # 保存结果
    if large_subgraphs:
        save_to_json(large_subgraphs)
    else:
        print("未找到节点数量大于 10 的子图。")

if __name__ == "__main__":
    main()