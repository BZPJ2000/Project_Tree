# dependency_analyzer/graph_builder.py
import networkx as nx


def build_dependency_graph(modules, dependencies):
    """构建依赖关系图"""
    graph = nx.DiGraph()

    # 添加节点
    for path in modules.values():
        graph.add_node(path)

    # 添加边
    for source, targets in dependencies.items():
        for target in targets:
            graph.add_edge(source, target)

    return graph