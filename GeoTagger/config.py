import os
from datetime import datetime

APP_NAME = "GeoTagger"
APP_VERSION = "1.0.0"

# Страницы / UI
DEFAULT_STYLE = "ui/style.qss"
ICON_APP = ":/icons/app_icon.png"

# Каталоги
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Лог файл
LOG_FILE = os.path.join(
    LOG_DIR, f"geotag_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
