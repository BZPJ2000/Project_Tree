# dependency_analyzer/module_collector.py
import os


def collect_modules(project_root):
    """收集项目中的所有Python模块"""
    modules = {}
    for root, dirs, files in os.walk(project_root):
        # 排除__pycache__
        if "__pycache__" in dirs:
            dirs.remove("__pycache__")

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                module_name = get_module_name(file_path, project_root)
                modules[module_name] = file_path
    return modules


def get_module_name(file_path, project_root):
    """将文件路径转换为模块名"""
    rel_path = os.path.relpath(file_path, project_root)

    if rel_path == "__init__.py":
        return ""

    dir_part, file_part = os.path.split(rel_path)

    if file_part == "__init__.py":
        # 处理包目录
        return dir_part.replace(os.sep, ".")

    # 处理普通Python文件
    module_path = rel_path[:-3].replace(os.sep, ".")
    return module_path.rstrip(".")