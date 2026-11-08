import os
import random
import re
import shutil
import uuid

from playwright.sync_api import Page, sync_playwright

PATH_TO_VIDEO_FOLDER = "./video"

SELECT_SEARCH = 'textarea[name="q"]'
SELECT_SUBMIT = 'form button[type="submit"]'
SELECT_FIRST_HIT = 'a[data-testid="result-title-a"]'

_VIDEO_W = 1280
_VIDEO_H = 720

_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_DIR, "overlay_init.js"), encoding="utf-8") as _f:
    OVERLAY_JS = _f.read()


def _video_basename(company: str) -> str:
    name = re.sub(r'[<>:"/\\\\|?*]', "_", company).strip()
    return name or "video"


def _center(box: dict) -> tuple[float, float]:
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


def _use_headless() -> bool:
    mode = os.environ.get("PLAYWRIGHT_HEADLESS", "auto").lower()
    if mode in ("0", "false", "no"):
        return False
    if mode in ("1", "true", "yes"):
        return True
    return not os.environ.get("DISPLAY")


def overlay(page: Page) -> None:
    try:
        page.evaluate(OVERLAY_JS)
    except Exception as err:
        if "destroyed" not in str(err).lower():
            raise
        page.wait_for_load_state("domcontentloaded", timeout=60_000)
        page.evaluate(OVERLAY_JS)


def move_cursor(page: Page, x0: float, y0: float, x1: float, y1: float) -> None:
    overlay(page)
    steps = 24
    for step in range(1, steps + 1):
        t = step / steps
        t = t * t * (3 - 2 * t)
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t
        page.mouse.move(x, y)
        page.evaluate("([px, py]) => window.__setCursorPosition(px, py)", [x, y])
        page.wait_for_timeout(12)


def ripple(page: Page, x: float, y: float) -> None:
    try:
        overlay(page)
        page.evaluate("([px, py]) => window.__playRipple(px, py)", [x, y])
    except Exception:
        pass


def callout(page: Page, text: str) -> None:
    page.evaluate(
        "(t) => window.ShowCallout(t, '#ffff00', '#000000', true)",
        text,
    )


def type_slow(page: Page, text: str) -> None:
    page.locator(SELECT_SEARCH).click()
    page.wait_for_timeout(200)
    for ch in text:
        page.keyboard.type(ch, delay=random.randint(60, 140))


def click_at(page: Page, locator, cx: float, cy: float, dom_click: bool = False) -> tuple[float, float]:
    box = locator.bounding_box()
    if not box:
        ripple(page, cx, cy)
        if dom_click:
            locator.evaluate("el => el.click()")
        else:
            locator.click()
        return cx, cy
    tx, ty = _center(box)
    move_cursor(page, cx, cy, tx, ty)
    ripple(page, tx, ty)
    if dom_click:
        locator.evaluate("el => el.click()")
    else:
        locator.click(timeout=5_000)
    page.wait_for_timeout(80)
    ripple(page, tx, ty)
    return tx, ty


def run_search(page: Page, query: str, cx: float, cy: float) -> tuple[float, float] | None:
    search = page.locator(SELECT_SEARCH)
    search.wait_for(state="visible", timeout=30_000)
    box = search.bounding_box()
    if not box:
        return None
    cx, cy = _center(box)
    move_cursor(page, 160, 200, cx, cy)
    ripple(page, cx, cy)

    search.fill("")
    type_slow(page, query)
    page.wait_for_timeout(300)

    submit = page.locator(SELECT_SUBMIT).first
    cx, cy = click_at(page, submit, cx, cy, dom_click=True)

    try:
        page.wait_for_url("**/*q=*", timeout=25_000)
    except Exception:
        search.press("Enter")
        page.wait_for_url("**/*q=*", timeout=40_000)

    overlay(page)
    return cx, cy


def open_first_hit(page: Page, cx: float, cy: float) -> bool:
    hit = page.locator(SELECT_FIRST_HIT).first
    hit.wait_for(state="visible", timeout=60_000)
    hit.scroll_into_view_if_needed()
    page.wait_for_timeout(300)
    overlay(page)

    box = hit.bounding_box()
    if not box:
        return False
    tx, ty = _center(box)
    move_cursor(page, cx, cy, tx, ty)
    ripple(page, tx, ty)

    href = hit.get_attribute("href")
    before = page.url
    try:
        with page.expect_navigation(timeout=45_000, wait_until="domcontentloaded"):
            hit.click(timeout=10_000)
    except Exception:
        pass

    if page.url == before and href:
        page.goto(href, wait_until="domcontentloaded", timeout=60_000)

    ripple(page, tx, ty)
    page.wait_for_timeout(2000)
    return page.url != before or bool(href)


def CaptureVideo_Magento(
    url: str,
    company_name: str,
    language: str,
    country: str,
    postcode: str,
    city: str,
    street: str,
    house_no: str,
) -> str | None:
    del language, country, postcode, street, house_no

    query = f"Magento developer in {city}"
    video_dir = os.path.abspath(os.path.expanduser(PATH_TO_VIDEO_FOLDER))
    os.makedirs(video_dir, exist_ok=True)
    dest = os.path.join(video_dir, f"{_video_basename(company_name)}.webm")
    tmp_dir = os.path.join(video_dir, f".tmp-{uuid.uuid4().hex}")

    try:
        os.makedirs(tmp_dir, exist_ok=True)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                headless=_use_headless(),
                args=["--disable-blink-features=AutomationControlled"],
            )
            context = browser.new_context(
                record_video_dir=tmp_dir,
                record_video_size={"width": _VIDEO_W, "height": _VIDEO_H},
                viewport={"width": _VIDEO_W, "height": _VIDEO_H},
            )
            page = context.new_page()

            page.goto(url, wait_until="domcontentloaded", timeout=60_000)
            page.wait_for_timeout(1000)
            overlay(page)
            page.mouse.move(160, 200)
            page.evaluate("([x, y]) => window.__setCursorPosition(x, y)", [160, 200])
            callout(page, f"Demo for {company_name}")
            page.wait_for_timeout(400)

            cursor = run_search(page, query, 160, 200)
            if cursor is None:
                return None
            cx, cy = cursor

            callout(page, "Opening first result")
            page.wait_for_timeout(600)
            if not open_first_hit(page, cx, cy):
                return None

            video = page.video
            page.close()
            context.close()
            browser.close()
            raw_path = video.path() if video else None

        if not raw_path or not os.path.isfile(raw_path):
            webms = [f for f in os.listdir(tmp_dir) if f.endswith(".webm")]
            if not webms:
                return None
            raw_path = os.path.join(tmp_dir, max(webms, key=lambda n: os.path.getmtime(os.path.join(tmp_dir, n))))

        if os.path.isfile(dest):
            os.remove(dest)
        shutil.move(raw_path, dest)
        return os.path.abspath(dest)

    except Exception:
        return None
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
