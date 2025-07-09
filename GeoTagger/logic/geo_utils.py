from timezonefinder import TimezoneFinder
import pytz


def get_timezone(lat: float, lon: float):
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon)
    if tz_name:
        return pytz.timezone(tz_name)
    return None


def coords_to_string(lat: float, lon: float) -> str:
    return f"{lat:.6f}, {lon:.6f}"
