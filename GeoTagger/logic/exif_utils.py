import os
import subprocess
from logic.logger import get_logger
from logic.config import get_exiftool_path

logger = get_logger()


def find_exiftool():
    # Сначала проверяем сохранённый путь
    configured_path = get_exiftool_path()
    if configured_path and os.path.exists(configured_path):
        logger.info(f"Используем сохранённый exiftool: {configured_path}")
        return configured_path

    # Если нет, ищем в проекте
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for root, dirs, files in os.walk(project_dir):
        for name in ["exiftool.exe", "exiftool(-k).exe", "exiftool"]:
            if name in files:
                full = os.path.join(root, name)
                logger.info(f"Найден exiftool в проекте: {full}")
                return full

    # Если нет, пробуем в PATH
    try:
        result = subprocess.run(["exiftool", "-ver"],
                                capture_output=True, text=True,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        logger.info(f"ExifTool найден в PATH: v{result.stdout.strip()}")
        return "exiftool"
    except Exception:
        logger.error(
            "❌ ExifTool не найден. Убедитесь, что он находится рядом с программой.")
        return None
