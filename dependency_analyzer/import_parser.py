# dependency_analyzer/import_parser.py
import ast
import os


def parse_dependencies(modules, project_root):
    """解析所有模块的依赖关系"""
    dependencies = {}
    for module_name, file_path in modules.items():
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read())
            except:
                continue

        deps = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dep_module = alias.name.split(".")[0]
                    if dep_module in modules:
                        deps.add(dep_module)

            elif isinstance(node, ast.ImportFrom):
                if node.level > 0:  # 处理相对导入
                    dep_module = resolve_relative_import(
                        module_name, node.level, node.module
                    )
                else:
                    dep_module = node.module

                if dep_module and dep_module in modules:
                    deps.add(dep_module)

        dependencies[file_path] = [
            modules[dep] for dep in deps if dep in modules
        ]
    return dependencies


def resolve_relative_import(current_module, level, module_name):
    """解析相对导入为绝对模块名"""
    if not current_module:
        return None

    parts = current_module.split(".")
    if level > len(parts):
        return None

    base = parts[: len(parts) - level + 1]
    if module_name:
        return ".".join(base + [module_name])
    return ".".join(base)