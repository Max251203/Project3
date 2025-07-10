import os
import json
from logic.logger import get_logger

logger = get_logger()

_config_file = os.path.join(os.path.dirname(__file__), "exiftool_config.json")
EXIFTOOL_PATH = None


def load_exiftool_path_from_file():
    """Создаёт config, если нет, и валидирует путь"""
    global EXIFTOOL_PATH

    if not os.path.exists(_config_file):
        logger.warning(
            "Файл exiftool_config.json не найден. Будет создан позже.")
        return

    try:
        with open(_config_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            path = data.get("exiftool_path", "").strip()
            if path and os.path.exists(path):
                EXIFTOOL_PATH = path
                logger.info(f"Загружен путь ExifTool: {path}")
            else:
                EXIFTOOL_PATH = None
                logger.warning("Путь к ExifTool из конфига не существует.")
    except json.JSONDecodeError:
        logger.error("Файл конфигурации повреждён. Содержит невалидный JSON.")
        EXIFTOOL_PATH = None
    except Exception as e:
        logger.error(f"Ошибка загрузки пути ExifTool из файла: {e}")


def save_exiftool_path_to_file(path: str):
    """Сохраняет путь в JSON"""
    try:
        with open(_config_file, "w", encoding="utf-8") as f:
            json.dump({"exiftool_path": path}, f, indent=2)
        logger.info(f"ExifTool путь сохранён: {path}")
    except Exception as e:
        logger.error(f"Ошибка сохранения пути ExifTool: {e}")


def set_exiftool_path(path: str):
    global EXIFTOOL_PATH
    EXIFTOOL_PATH = path
    save_exiftool_path_to_file(path)


def get_exiftool_path() -> str | None:
    global EXIFTOOL_PATH
    return EXIFTOOL_PATH
