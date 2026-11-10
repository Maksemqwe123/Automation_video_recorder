FROM mcr.microsoft.com/playwright/python:v1.64.1-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY capture_video.py qscript.py overlay_init.js entrypoint.sh ./
RUN chmod +x /app/entrypoint.sh

ENV PLAYWRIGHT_HEADLESS=0

ENTRYPOINT ["/app/entrypoint.sh"]
