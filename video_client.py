import os

import requests


def UploadVideo(server_url: str, video_path: str, company_name: str) -> str:
    """Uploads a video file to the server and returns its URL."""
    endpoint = f"{server_url.rstrip('/')}/upload"
    filename = os.path.basename(video_path)
    with open(video_path, "rb") as fileobj:
        response = requests.post(
            endpoint,
            files={"file": (filename, fileobj, "video/webm")},
            data={"company_name": company_name},
            timeout=600,
        )
    response.raise_for_status()
    payload = response.json()
    return str(payload["video_url"])


def GetVideoURL(server_url: str, company_name: str) -> str:
    """Returns the video URL for the given company name."""
    endpoint = f"{server_url.rstrip('/')}/get_video_url"
    response = requests.get(
        endpoint,
        params={"company_name": company_name},
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    return str(payload["video_url"])
