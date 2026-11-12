import os
import re

_UNSAFE = re.compile(r'[<>:"/\\\\|?*\x00-\x1f]')


def safe_media_filename(company_name: str) -> str:
    base = _UNSAFE.sub("_", company_name.strip()) or "video"
    if not base.lower().endswith(".webm"):
        base = f"{base}.webm"
    return os.path.basename(base)
