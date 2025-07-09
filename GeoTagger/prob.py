import os


def print_project_structure(path, indent=0):
    try:
        entries = os.listdir(path)
        entries.sort()  # Сортируем для более предсказуемого вывода

        for index, entry in enumerate(entries):
            full_path = os.path.join(path, entry)
            if entry in ['__pycache__', '.git']:
                continue

            # Определяем символы для отображения вложенности
            connector = '├── ' if index < len(entries) - 1 else '└── '
            print('    ' * indent + connector + entry)

            if os.path.isdir(full_path):
                print_project_structure(full_path, indent + 1)
    except PermissionError:
        print('    ' * indent + '└── [Permission denied]')


if __name__ == "__main__":
    project_path = 'D:\Max\Project3\GeoTagger'  # Укажите путь к папке с проектом
    print_project_structure(project_path)
