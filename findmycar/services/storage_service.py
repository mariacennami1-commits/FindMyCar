import json
import os
from datetime import datetime
from kivy.logger import Logger
from kivy.utils import platform
from plyer import storagepath


class ParkingRecord:
    def __init__(self, latitude, longitude, address="", notes="", timestamp=None):
        self.id = None
        self.latitude = latitude
        self.longitude = longitude
        self.address = address
        self.notes = notes
        self.timestamp = timestamp or datetime.now().isoformat()
        self.photo_path = ""

    def to_dict(self):
        return {
            "id": self.id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "notes": self.notes,
            "timestamp": self.timestamp,
            "photo_path": self.photo_path,
        }

    @classmethod
    def from_dict(cls, data):
        record = cls(
            data["latitude"],
            data["longitude"],
            data.get("address", ""),
            data.get("notes", ""),
            data.get("timestamp"),
        )
        record.id = data.get("id")
        record.photo_path = data.get("photo_path", "")
        return record


class StorageService:
    def __init__(self):
        self._file_path = self._get_storage_path()
        self._records = []
        self._current_id = 0
        self._load()

    def _get_storage_path(self):
        if platform == "android":
            base = storagepath.get_external_storage_dir()
        elif platform == "ios":
            base = storagepath.get_documents_dir()
        else:
            base = os.path.join(os.path.expanduser("~"), ".findmycar")
            os.makedirs(base, exist_ok=True)
        return os.path.join(base, "parking_data.json")

    def _load(self):
        try:
            if os.path.exists(self._file_path):
                with open(self._file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._current_id = data.get("current_id", 0)
                    for item in data.get("records", []):
                        record = ParkingRecord.from_dict(item)
                        self._records.append(record)
                Logger.info(f"StorageService: Loaded {len(self._records)} records")
        except Exception as e:
            Logger.error(f"StorageService: Load error - {e}")
            self._records = []
            self._current_id = 0

    def _save(self):
        try:
            data = {
                "current_id": self._current_id,
                "records": [r.to_dict() for r in self._records],
            }
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            Logger.error(f"StorageService: Save error - {e}")

    def save_parking(self, latitude, longitude, address="", notes=""):
        record = ParkingRecord(latitude, longitude, address, notes)
        self._current_id += 1
        record.id = self._current_id
        self._records.append(record)
        self._save()
        Logger.info(f"StorageService: Saved parking #{record.id}")
        return record

    def get_latest(self):
        if self._records:
            return self._records[-1]
        return None

    def get_all(self):
        return list(reversed(self._records))

    def get_by_id(self, record_id):
        for r in self._records:
            if r.id == record_id:
                return r
        return None

    def delete(self, record_id):
        self._records = [r for r in self._records if r.id != record_id]
        self._save()

    def clear_all(self):
        self._records = []
        self._current_id = 0
        self._save()
