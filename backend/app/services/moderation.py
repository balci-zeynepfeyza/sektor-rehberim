from __future__ import annotations

import re


_TURKISH_CHAR_MAP: dict[str, str] = {
    "ç": "c",
    "ğ": "g",
    "ı": "i",
    "ö": "o",
    "ş": "s",
    "ü": "u",
}

# MVP için kaba/kısa bir küfür-hakaret örnek listesidir.
# İleride bunu bir “özel kelime listesi + yönetim ekranı” ile zenginleştireceğiz.
_PROFANITY_STRINGS: tuple[str, ...] = (
    "orospu",
    "piç",
    "sik",
    "amk",
)

_LEET_MAP: dict[str, str] = {
    "0": "o",
    "1": "i",
    "3": "e",
    "4": "a",
    "5": "s",
    "7": "t",
}


def _normalize_for_filter(message: str) -> tuple[str, str]:
    normalized = message.lower()
    for k, v in _TURKISH_CHAR_MAP.items():
        normalized = normalized.replace(k, v)

    for k, v in _LEET_MAP.items():
        normalized = normalized.replace(k, v)

    # Sadece harf/rakam bırak; kelimeleri kompaktlaştırarak "a m k" gibi yazımları yakalamayı kolaylaştır.
    letters_and_digits = re.sub(r"[^a-z0-9]+", " ", normalized)
    compact = re.sub(r"[^a-z0-9]+", "", normalized)

    compact = compact.strip()
    return letters_and_digits, compact


def contains_profanity(message: str) -> bool:
    if not message:
        return False

    _, compact = _normalize_for_filter(message)
    if not compact:
        return False

    for term in _PROFANITY_STRINGS:
        # term kendisi türkçe karakter içerebilir; compact'te türkçe karakterler normalize edildiği için ayrıca normalize ediyoruz.
        term_norm = term.lower()
        for k, v in _TURKISH_CHAR_MAP.items():
            term_norm = term_norm.replace(k, v)

        if term_norm in compact:
            return True

    return False

