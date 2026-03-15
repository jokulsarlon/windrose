# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QObject, pyqtSignal
import requests
import numpy as np
import calendar

from .windrose_utils import compute_frequencies


class WindRoseWorker(QObject):
    finished = pyqtSignal(object, object, object)  # freq, labels, angles
    error = pyqtSignal(str)

    def __init__(self, lon, lat, year, month, height):
        super().__init__()
        self.lon = lon
        self.lat = lat
        self.year = year
        self.month = month
        self.height = height

    def run(self):
        try:
            wd_list = self.fetch_wind_data()
            freq, labels, angles = compute_frequencies(wd_list)
            self.finished.emit(freq, labels, angles)
        except Exception as e:
            self.error.emit(str(e))

    def fetch_wind_data(self):
        url = "https://archive-api.open-meteo.com/v1/archive"
        if self.month is None:
            start_date = f"{self.year}-01-01"
            end_date = f"{self.year}-12-31"
        else:
            last_day = calendar.monthrange(self.year, self.month)[1]
            start_date = f"{self.year}-{self.month:02d}-01"
            end_date = f"{self.year}-{self.month:02d}-{last_day:02d}"

        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": f"wind_direction_{self.height}m",
            "timezone": "auto",
            "models": "era5"
        }
        try:
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            key = f"wind_direction_{self.height}m"
            if "hourly" not in data or key not in data["hourly"]:
                raise Exception(f"未找到风向数据（高度{self.height}m可能不支持）")
            wd = data["hourly"][key]
            wd = [x for x in wd if x is not None]
            if not wd:
                raise Exception("风向数据全部为空")
            return wd
        except requests.exceptions.RequestException as e:
            raise Exception(f"API请求失败: {e}")