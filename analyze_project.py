# analyze_project.py
import os
import argparse
from dependency_analyzer.module_collector import collect_modules
from dependency_analyzer.import_parser import parse_dependencies
from dependency_analyzer.graph_builder import build_dependency_graph
from dependency_analyzer.print_directory_structure import print_directory_structure
from dependency_analyzer.visualizer import visualize_graph



def main():
    parser = argparse.ArgumentParser(description="Python项目依赖分析工具")
    parser.add_argument("project_path", help="Python项目根目录路径")
    parser.add_argument("-o", "--output", default="dependency_graph.png", help="输出图片路径")
    parser.add_argument("--print-structure", action="store_true", help="打印项目目录结构")
    parser.add_argument("--output-format", choices=["text", "json"], default="text",
                        help="输出数据格式，可选text或json")
    args = parser.parse_args()

    if args.print_structure:
        print_directory_structure(args.project_path)

        # 收集模块信息
    modules = collect_modules(args.project_path)

    # 解析依赖关系
    dependencies = parse_dependencies(modules, args.project_path)

    # 构建依赖图
    graph = build_dependency_graph(modules, dependencies)

    if args.output_format == "text":
        print("模块信息:")
        for module in modules:
            print(module)
        print("\n依赖关系:")
        for dep in dependencies:
            print(dep)
        print("\n依赖图:")
        print(graph)
    elif args.output_format == "json":
        import json
        module_info = [vars(module) for module in modules]
        dep_info = [{"source": dep[0].__name__, "target": dep[1].__name__} for dep in dependencies]
        graph_info = {node.__name__: [neighbor.__name__ for neighbor in neighbors] for node, neighbors in graph.items()}
        output_data = {
            "modules": module_info,
            "dependencies": dep_info,
            "graph": graph_info
        }
        print(json.dumps(output_data, indent=4))

        # 可视化
    visualize_graph(graph, args.project_path, args.output)
    print(f"依赖图保存至: {args.output}")


if __name__ == "__main__":
    main()