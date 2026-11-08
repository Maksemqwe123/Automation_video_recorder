# CSV-driven Browser Automation Video Recorder

Python + Playwright: one `.webm` per CSV row.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```

## Run

```bash
python capture_video.py
```

Видео: `./video/<Company Name>.webm`. При необходимости: `PLAYWRIGHT_HEADLESS=0`.

## Files

- `capture_video.py` — `input.csv`, цикл по строкам
- `qscript.py` — `CaptureVideo_Magento`, `PATH_TO_VIDEO_FOLDER`
- `overlay_init.js` — курсор / ripple / callout
- `input.csv` — входные данные
