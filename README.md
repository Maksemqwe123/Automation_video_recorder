# CSV-driven Browser Automation Video Recorder

Python + Playwright: one `.webm` per CSV row.

## Запуск с окном браузера (рекомендуется на рабочем столе)

Docker по умолчанию **показывает окно Chromium на экране**, если из терминала проброшен `DISPLAY` (см. `docker-compose.yml`).

Один раз разрешите контейнеру доступ к X11:

```bash
xhost +local:docker
docker compose build
docker compose run --rm recorder
```

Если окно не появилось (SSH без GUI, CI) — принудительно без окна, через Xvfb:

```bash
docker compose run --rm -e USE_XVFB=1 recorder
```

**Без Docker** — то же самое в обычном окне:

```bash
source .venv/bin/activate
PLAYWRIGHT_HEADLESS=0 python capture_video.py
```

(При `PLAYWRIGHT_HEADLESS=auto` и настроенном `DISPLAY` окно тоже откроется.)

Готовые ролики: `./video/<Company Name>.webm`. На строку CSV обычно 1–3 минуты.

## Локальная установка

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```

## Files

- `capture_video.py` — `input.csv`, цикл по строкам
- `qscript.py` — `CaptureVideo_Magento`, `PATH_TO_VIDEO_FOLDER`
- `overlay_init.js` — курсор / ripple / callout
- `input.csv` — входные данные
- `Dockerfile`, `docker-compose.yml`, `entrypoint.sh` — Docker
