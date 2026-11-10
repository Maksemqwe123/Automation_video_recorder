#!/bin/sh
set -e

if [ "$USE_XVFB" = "1" ] || [ -z "$DISPLAY" ]; then
  exec xvfb-run -a --server-args="-screen 0 1280x720x24" python capture_video.py
fi

exec python capture_video.py
