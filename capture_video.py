import argparse
import csv
import os
import sys

import qscript

_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_CSV = os.path.join(_DIR, "input.csv")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record demo videos from input.csv")
    parser.add_argument(
        "--server",
        metavar="URL",
        default=None,
        help="After each recording, upload to this base URL (e.g. http://127.0.0.1:5000)",
    )
    parser.add_argument(
        "--view-seconds",
        type=int,
        default=5,
        help="Preview uploaded video in Chromium: seconds to wait (>0), or 0 to wait for Enter",
    )
    return parser.parse_args(argv)


def _preview_uploaded_video(video_url: str, view_seconds: int) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        try:
            page = browser.new_page()
            page.goto(video_url, wait_until="domcontentloaded", timeout=120_000)
            if view_seconds > 0:
                page.wait_for_timeout(view_seconds * 1000)
            else:
                input("Preview open — press Enter to continue...")
        finally:
            browser.close()


def _upload_and_preview(
    server_url: str,
    video_path: str,
    company_name: str,
    view_seconds: int,
) -> None:
    from video_client import UploadVideo

    video_url = UploadVideo(server_url, video_path, company_name)
    print(f"Uploaded {company_name}: {video_url}")
    _preview_uploaded_video(video_url, view_seconds)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    qscript.PATH_TO_VIDEO_FOLDER = os.path.join(_DIR, "uploads")
    os.makedirs(qscript.PATH_TO_VIDEO_FOLDER, exist_ok=True)

    if not os.path.isfile(INPUT_CSV):
        print(f"Missing CSV: {INPUT_CSV}", file=sys.stderr)
        return 1

    with open(INPUT_CSV, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=";", quotechar='"')
        for row in reader:
            company = row["Company Name"].strip()
            path = qscript.CaptureVideo_Magento(
                row["URL"].strip(),
                company,
                row["Language"].strip(),
                row["Country"].strip(),
                row["Postcode"].strip(),
                row["City"].strip(),
                row["Street"].strip(),
                row["HouseNo"].strip(),
            )
            if not path:
                print(f"Failed: {company}", file=sys.stderr)
                continue

            print(path)
            if not args.server:
                continue

            try:
                _upload_and_preview(args.server, path, company, args.view_seconds)
            except Exception as err:
                print(f"Upload/preview failed for {company}: {err}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
