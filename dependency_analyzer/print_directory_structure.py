import ast
import os


def find_imported_files(file_path, project_path):
    imported_files = []
    with open(file_path, 'r', encoding='utf-8') as file:
        tree = ast.parse(file.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    module_name = alias.name
                    if '.' in module_name:
                        module_name = module_name.split('.')[0]
                    for root, dirs, files in os.walk(project_path):
                        for file in files:
                            if file.endswith('.py') and file[:-3] == module_name:
                                imported_files.append(os.path.join(root, file))
    return imported_files


def get_all_relevant_files(project_path):
    relevant_files = []
    queue = []
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                relevant_files.append(file_path)
                queue.append(file_path)

    while queue:
        current_file = queue.pop(0)
        imported_files = find_imported_files(current_file, project_path)
        for imported_file in imported_files:
            if imported_file not in relevant_files:
                relevant_files.append(imported_file)
                queue.append(imported_file)

    return relevant_files


def print_directory_structure(project_path):
    relevant_files = get_all_relevant_files(project_path)
    for root, dirs, files in os.walk(project_path):
        level = root.replace(project_path, '').count(os.sep)
        indent = ' ' * 4 * level
        print(f"{indent}{os.path.basename(root)}/")  # 始终显示目录结构
        sub_indent = ' ' * 4 * (level + 1)

        for file in files:
            file_path = os.path.join(root, file)
            if file_path in relevant_files and file.endswith('.py'):
                print(f"{sub_indent}{file}")
