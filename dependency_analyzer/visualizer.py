import os
import math
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import patheffects

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']

# 科研论文级配色方案
COLOR_SCHEME = {
    "background": "#F7F9FC",
    "primary": "#2E5984",
    "secondary": "#48A9A6",
    "tertiary": "#C4D6B0",
    "edge": "#9FA8DA",
    "text": "#2B2B2B"
}


def visualize_graph(graph, project_root, output_path):
    """高级可视化引擎"""
    plt.figure(figsize=(24, 18), facecolor=COLOR_SCHEME["background"])
    plt.rcParams['font.family'] = 'DejaVu Sans'

    # 构建布局数据
    depth_levels = calculate_depth_levels(graph, project_root)
    nx.set_node_attributes(graph, depth_levels, 'layer')

    node_metrics = calculate_node_metrics(graph)
    pos = create_hybrid_layout(graph)

    # 重要修改点：获取节点绘图对象
    ax = plt.gca()
    draw_edges(graph, pos)
    node_collection = draw_nodes(graph, pos, depth_levels, node_metrics)  # 获取绘图返回值
    draw_labels(graph, pos, project_root)

    # 传递绘图对象给颜色条
    add_color_bar(node_collection, depth_levels)
    add_legend(node_metrics)

    plt.title("Project  Dependency Analysis\n", fontsize=18, color=COLOR_SCHEME["text"], pad=20)
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()


def calculate_depth_levels(graph, project_root):
    """计算并返回节点深度字典"""
    return {
        node: len(os.path.relpath(node, project_root).split(os.sep))
        for node in graph.nodes
    }


def calculate_node_metrics(graph):
    """计算节点重要指标"""
    return {
        "degree": dict(graph.degree()),
        "betweenness": nx.betweenness_centrality(graph)
    }


def create_hybrid_layout(graph):
    """创建混合布局系统"""
    # 基础层级布局（需要先设置layer属性）
    base_pos = nx.multipartite_layout(graph, subset_key="layer")

    # 力导向优化
    return nx.spring_layout(
        graph,
        pos=base_pos,
        k=2.5 / math.sqrt(len(graph.nodes)),
        iterations=200,
        threshold=0.0001
    )


def draw_edges(graph, pos):
    """绘制优化边"""
    edge_colors = []
    for (u, v) in graph.edges():
        distance = math.dist(pos[u], pos[v])
        edge_colors.append(0.7 - min(distance / 8, 0.5))

    nx.draw_networkx_edges(
        graph, pos,
        edge_color=edge_colors,
        edge_cmap=plt.cm.Blues,
        width=0.8,
        alpha=0.4,
        arrowsize=22,
        arrowstyle='-|>',
        connectionstyle='arc3,rad=0.15',
        min_source_margin=15,
        min_target_margin=15
    )


def draw_nodes(graph, pos, depth_levels, metrics):
    """返回节点绘图对象"""
    max_depth = max(depth_levels.values()) or 1
    cmap = LinearSegmentedColormap.from_list("depth", [
        COLOR_SCHEME["primary"],
        COLOR_SCHEME["secondary"],
        COLOR_SCHEME["tertiary"]
    ])

    # 构造颜色映射
    node_colors = [cmap(l / max_depth) for l in depth_levels.values()]
    node_sizes = [600 + 800 * metrics["betweenness"][n] for n in graph.nodes]

    # 返回绘图对象
    return nx.draw_networkx_nodes(
        graph, pos,
        node_size=node_sizes,
        node_color=node_colors,
        edgecolors=COLOR_SCHEME["text"],
        linewidths=0.5,
        alpha=0.9
    )

class LabelManager:
    """智能标签管理系统"""

    def __init__(self):
        self.label_cache = {}
        self.counter = {}

    def generate_unique_label(self, path):
        # 实现路径智能压缩算法
        compressed = self.path_compression(path)

        # 确保唯一性检测
        if compressed in self.label_cache.values():
            return self.resolve_conflict(path, compressed)

        self.label_cache[path] = compressed
        return compressed

    @staticmethod
    def path_compression(path, max_length=40):
        """路径智能压缩算法"""
        parts = path.split(os.sep)

        # 专家级路径压缩规则：
        if len(parts) > 4:
            mid = f"{parts[0]}/.../{parts[-3]}/{parts[-2]}/{parts[-1]}"
        elif len(parts) > 3:
            mid = f"{parts[0]}/{parts[1]}/.../{parts[-1]}"
        else:
            mid = path

        # 自动换行优化
        return '\n'.join([
            mid[i:i + 20] for i in range(0, min(len(mid), max_length), 20)
        ])

    def resolve_conflict(self, original_path, compressed):
        """冲突解决算法加强版"""
        conflict_count = self.counter.get(compressed, 0) + 1
        self.counter[compressed] = conflict_count

        # 增加唯一性保障层级
        parent_dir = os.path.basename(os.path.dirname(original_path)) or os.path.basename(original_path)
        unique_marker = f"{parent_dir[:5]}-{conflict_count}"
        return f"{compressed}\n({unique_marker})"

def draw_labels(graph, pos, project_root):
    """优化标签生成系统"""
    label_manager = LabelManager()
    labels = {}

    for node in graph.nodes:
        rel_path = os.path.relpath(node, project_root)
        labels[node] = label_manager.generate_unique_label(rel_path)

    # 保留原始文字渲染逻辑
    text = nx.draw_networkx_labels(
        graph, pos,
        labels=labels,
        font_size=8,
        font_color=COLOR_SCHEME["text"],
        verticalalignment='center'
    )

    # 添加抗锯齿特效
    for _, t in text.items():
        t.set_path_effects([
            patheffects.withStroke(
                linewidth=2,
                foreground=COLOR_SCHEME["background"]
            )
        ])




def add_color_bar(node_collection, depth_levels):
    """基于实际节点着色创建颜色条"""
    cmap = LinearSegmentedColormap.from_list("depth", [
        COLOR_SCHEME["primary"],
        COLOR_SCHEME["secondary"],
        COLOR_SCHEME["tertiary"]
    ])

    # 专业级的颜色条设置
    cbar = plt.colorbar(
        node_collection,
        orientation='vertical',
        shrink=0.3,
        aspect=30,
        pad=0.01,
        cmap=cmap,
        boundaries=range(min(depth_levels.values()), max(depth_levels.values()) + 1)
    )

    # 设置刻度标签
    max_depth = max(depth_levels.values())
    cbar.set_ticks([(i + 0.5) / (max_depth + 1) for i in range(max_depth + 1)])
    cbar.set_ticklabels(range(max_depth + 1))
    cbar.set_label('Directory  Depth', rotation=270, labelpad=25, fontsize=12)


def add_legend(metrics):
    """添加指标图例"""
    legend_elements = [
        plt.Line2D([], [],
                   marker='o',
                   color='w',
                   markerfacecolor=COLOR_SCHEME["primary"],
                   markersize=15,
                   label='Core Modules (High Betweenness)'),
        plt.Line2D([], [],
                   marker='o',
                   color='w',
                   markerfacecolor=COLOR_SCHEME["tertiary"],
                   markersize=8,
                   label='Edge Modules')
    ]
    plt.legend(
        handles=legend_elements,
        loc='upper left',
        frameon=True,
        framealpha=0.9
    )