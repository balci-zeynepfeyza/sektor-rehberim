from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_data_dir: str
    sqlite_path: str
    anon_names: tuple[str, ...]


def get_settings() -> Settings:
    app_data_dir = os.getenv("APP_DATA_DIR", os.path.join("backend", "data"))
    sqlite_path = os.getenv("SQLITE_PATH", os.path.join(app_data_dir, "app.db"))

    raw_names = os.getenv(
        "ANON_NAMES",
        ",".join(
            [
                "Mersinli Mühendis",
                "Junior Dev",
                "Stajyer Avcısı",
                "Kod Şairi",
                "Sistemci",
                "Backend Meraklısı",
                "Frontend Gezgin",
                "QA Kaptanı",
                "DevOps Yolcusu",
                "Algoritma Dostu",
            ]
        ),
    )
    anon_names = tuple(n.strip() for n in raw_names.split(",") if n.strip())
    if not anon_names:
        anon_names = ("Anonim",)

    return Settings(
        app_data_dir=app_data_dir,
        sqlite_path=sqlite_path,
        anon_names=anon_names,
    )

