from __future__ import annotations

import secrets

from backend.app.core.config import Settings


def pick_anon_name(settings: Settings) -> str:
    # Server-side randomization ensures we don't rely on client behavior.
    return secrets.choice(settings.anon_names)

