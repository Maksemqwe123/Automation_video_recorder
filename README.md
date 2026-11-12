# Automation Video Recorder

Запись демо-видео из `input.csv` (Playwright). Flask-сервис сохраняет `.webm` и отдаёт по URL.

## Быстрый старт

```bash
pip install -r requirements.txt
python -m playwright install chromium
python web_service.py
```

Во втором терминале:

```bash
python capture_video.py --server http://127.0.0.1:8000
```

В браузере: `http://127.0.0.1:8000/videos` или URL из ответа `/upload`.

## API

| Method | Path |
|--------|------|
| POST | `/upload` |
| GET | `/get_video_url?company_name=...` |
| GET | `/media/<filename>` |
| GET | `/videos` |
