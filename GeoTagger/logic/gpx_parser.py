from datetime import datetime
import gpxpy
from timezonefinder import TimezoneFinder
import pytz


def parse_gpx_metadata(file_path: str) -> dict:
    """Парсит GPX и возвращает начальное и конечное время, и местное время старта"""

    with open(file_path, "r", encoding="utf-8") as f:
        gpx = gpxpy.parse(f)

    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                if point.time:
                    points.append(point)

    if not points:
        raise ValueError("В GPX-файле не найдено ни одной точки с временем")

    # Определим стартовую и конечную точку
    first_point = points[0]
    last_point = points[-1]

    # Время в UTC
    start_utc = first_point.time
    end_utc = last_point.time

    # Получаем временную зону по координатам
    tz = get_timezone(first_point.latitude, first_point.longitude)
    tzname = tz.zone if tz else "UTC"

    # Переводим стартовое UTC в локальное по координатам
    start_local = start_utc.astimezone(tz).strftime(
        "%Y-%m-%d %H:%M:%S") if tz else "—"
    start_utc_str = start_utc.strftime("%Y-%m-%d %H:%M:%S")
    end_utc_str = end_utc.strftime("%Y-%m-%d %H:%M:%S")

    return {
        "start": start_utc_str,
        "end": end_utc_str,
        "start_local": start_local,
        "timezone": tzname,
    }


def get_timezone(lat: float, lon: float):
    """Определяет часовой пояс по координатам"""
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lat=lat, lng=lon)
    if timezone_str:
        return pytz.timezone(timezone_str)
    return None
