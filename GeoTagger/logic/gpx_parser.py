from datetime import datetime
import gpxpy
from logic.geo_utils import get_timezone
from logic.logger import get_logger

# Инициализация логгера
logger = get_logger()


def parse_gpx_metadata(gpx_path: str) -> dict:
    """Парсит GPX и возвращает начальное и конечное время, и местное время старта"""
    logger.info(f"Анализ GPX-файла: {gpx_path}")

    with open(gpx_path, "r", encoding="utf-8") as f:
        gpx = gpxpy.parse(f)

    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                if point.time:
                    points.append(point)

    if not points:
        logger.error("В GPX-файле не найдено ни одной точки с временем")
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

    # Проверяем, пересекает ли трек несколько часовых поясов
    timezone_warning = check_multiple_timezones(points)

    logger.info(
        f"Трек начинается: {start_utc_str} UTC, заканчивается: {end_utc_str} UTC")
    logger.info(f"Местное время старта: {start_local} ({tzname})")

    if timezone_warning:
        logger.warning(
            "Трек пересекает несколько часовых поясов. Используется зона старта.")

    return {
        "start": start_utc_str,
        "end": end_utc_str,
        "start_local": start_local,
        "timezone": tzname,
        "timezone_warning": timezone_warning
    }


def check_multiple_timezones(points):
    """Проверяет, пересекает ли трек несколько часовых поясов"""
    if len(points) < 2:
        return False

    # Берем первую и последнюю точки
    first_point = points[0]
    last_point = points[-1]

    # Получаем временные зоны
    first_tz = get_timezone(first_point.latitude, first_point.longitude)
    last_tz = get_timezone(last_point.latitude, last_point.longitude)

    # Если зоны разные, возвращаем True
    if first_tz and last_tz and first_tz.zone != last_tz.zone:
        return True

    return False


def analyze_gpx_file(gpx_path: str):
    """Анализирует GPX-файл и возвращает информацию о нем"""
    logger.info(f"Детальный анализ GPX-файла: {gpx_path}")

    try:
        with open(gpx_path, "r", encoding="utf-8") as f:
            gpx = gpxpy.parse(f)

        # Общая информация
        track_count = len(gpx.tracks)
        segment_count = sum(len(track.segments) for track in gpx.tracks)
        point_count = sum(sum(len(segment.points)
                          for segment in track.segments) for track in gpx.tracks)

        # Точки с временем
        points_with_time = sum(sum(sum(1 for point in segment.points if point.time)
                                   for segment in track.segments) for track in gpx.tracks)

        # Временной диапазон
        all_points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    if point.time:
                        all_points.append(point)

        if all_points:
            all_points.sort(key=lambda p: p.time)
            time_range = (all_points[-1].time -
                          all_points[0].time).total_seconds()
            hours = int(time_range // 3600)
            minutes = int((time_range % 3600) // 60)
            seconds = int(time_range % 60)
            time_range_str = f"{hours}ч {minutes}м {seconds}с"
        else:
            time_range_str = "Нет точек с временем"

        # Географический охват
        if point_count > 0:
            min_lat = min(
                point.latitude for track in gpx.tracks for segment in track.segments for point in segment.points)
            max_lat = max(
                point.latitude for track in gpx.tracks for segment in track.segments for point in segment.points)
            min_lon = min(
                point.longitude for track in gpx.tracks for segment in track.segments for point in segment.points)
            max_lon = max(
                point.longitude for track in gpx.tracks for segment in track.segments for point in segment.points)
            geo_range = f"Широта: {min_lat:.6f} - {max_lat:.6f}, Долгота: {min_lon:.6f} - {max_lon:.6f}"
        else:
            geo_range = "Нет точек с координатами"

        logger.info(
            f"Треков: {track_count}, сегментов: {segment_count}, точек: {point_count}")
        logger.info(f"Точек с временем: {points_with_time}")
        logger.info(f"Временной диапазон: {time_range_str}")
        logger.info(f"Географический охват: {geo_range}")

        return {
            "track_count": track_count,
            "segment_count": segment_count,
            "point_count": point_count,
            "points_with_time": points_with_time,
            "time_range": time_range_str,
            "geo_range": geo_range
        }

    except Exception as e:
        logger.error(f"Ошибка при анализе GPX: {e}")
        return None
