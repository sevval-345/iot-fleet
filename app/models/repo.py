# app/models/repo.py
import pandas as pd
from sqlalchemy import text
from app.core.db import ENGINE
from app.services.utils import to_dt


class Repo:
    def __init__(self):
        self._ts = None
        # Bellekte tutulacak DataFrame’ler
        self.sims = pd.DataFrame()
        self.plans = pd.DataFrame()
        self.usage = pd.DataFrame()          # günlük veri (dbo.usage_30d)
        self.usage_hourly = pd.DataFrame()   # saatlik veri (dbo.usage_hourly)
        self.profiles = pd.DataFrame()
        self.addons = pd.DataFrame()

    def reload(self):
        """Tüm verileri DB’den yükler."""
        # SIM kartlar
        self.sims = pd.read_sql(text("SELECT * FROM dbo.sims"), ENGINE).set_index("sim_id", drop=False)

        # Planlar
        self.plans = pd.read_sql(text("SELECT * FROM dbo.iot_plans"), ENGINE).set_index("plan_id", drop=False)

        # Günlük kullanım (30 günlük pencere)
        self.usage = pd.read_sql(
            text("SELECT sim_id, timestamp_mb, mb_used, roaming_mb FROM dbo.usage_30d"),
            ENGINE
        )
        self.usage["timestamp_mb"] = to_dt(self.usage["timestamp_mb"])

        # Saatlik kullanım (opsiyonel tablo)
        try:
            self.usage_hourly = pd.read_sql(
                text("SELECT sim_id, timestamp_mb, mb_used, roaming_mb, sms_count FROM dbo.usage_hourly"),
                ENGINE
            )
            self.usage_hourly["timestamp_mb"] = to_dt(self.usage_hourly["timestamp_mb"])
        except Exception:
            self.usage_hourly = pd.DataFrame()

        # Cihaz profilleri
        try:
            self.profiles = pd.read_sql(text("SELECT * FROM dbo.device_profiles"), ENGINE)
        except Exception:
            self.profiles = pd.DataFrame()

        # Ek paketler
        try:
            self.addons = pd.read_sql(text("SELECT * FROM dbo.add_on_packs"), ENGINE)
        except Exception:
            self.addons = pd.DataFrame()

        # Bellekte veri güncellendi
        self._ts = pd.Timestamp.utcnow()

    def reload_if_stale(self, minutes: int = 5, force: bool = False):
        """Son yüklemeden belli süre geçtiyse DB’den tekrar yükle."""
        if force or self._ts is None:
            return self.reload()
        if (pd.Timestamp.utcnow() - self._ts).total_seconds() > minutes * 60:
            return self.reload()


# Tekil repo objesi
repo = Repo()
