import json
import mimetypes
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests

ENDPOINT = "https://sora.chatgpt.com/backend/project_y/file/upload"
OUTPUT_FILE = Path(__file__).with_name("sora_request.json")

# ================== DÁN ẢNH Ở ĐÂY ==================
# Ưu tiên dùng đường dẫn local trên máy.
LOCAL_IMAGE_PATH = r"D:\\Tiktok\\KOL\\KOL_new.png"
# Nếu muốn test bằng link online thì điền IMAGE_URL.
IMAGE_URL = ""

# Cấu hình upload (điền trực tiếp trong file, không nhập tay)
USE_CASE = "inpaint_safe"
AUTHORIZATION_TOKEN = ""  # wiped
COOKIE = ""
REQUEST_TIMEOUT = 120
# ====================================================


def _safe_filename_from_url(image_url: str) -> str:
    parsed = urlparse(image_url)
    name = Path(parsed.path).name.strip()
    if not name:
        return "upload_image"
    return name


def _guess_mime(filename: str, response_headers: dict) -> str:
    content_type = (response_headers or {}).get("Content-Type", "").split(";")[0].strip()
    if content_type:
        return content_type
    guessed, _ = mimetypes.guess_type(filename)
    return guessed or "application/octet-stream"


def _normalize_authorization_value(raw_token: str) -> str:
    token = str(raw_token or "").strip()
    if not token:
        return ""
    if token.lower().startswith("bearer "):
        return token
    return f"Bearer {token}"


def _mask_authorization(auth_value: str) -> str:
    value = str(auth_value or "").strip()
    if not value:
        return ""
    if len(value) <= 22:
        return "***"
    return f"{value[:14]}...{value[-8:]}"


def _download_image_bytes(image_url: str, timeout: int = 60):
    resp = requests.get(image_url, timeout=timeout)
    resp.raise_for_status()
    filename = _safe_filename_from_url(image_url)
    mime = _guess_mime(filename, dict(resp.headers))

    if "." not in filename:
        ext = mimetypes.guess_extension(mime) or ""
        filename = f"{filename}{ext}"

    return filename, mime, resp.content


def _read_image_source_bytes(image_source: str, timeout: int = 60):
    source = str(image_source or "").strip().strip('"').strip("'")
    if not source:
        raise ValueError("Thiếu nguồn ảnh")

    lowered = source.lower()
    if lowered.startswith("http://") or lowered.startswith("https://"):
        return _download_image_bytes(source, timeout=timeout)

    local_path = Path(source).expanduser()
    if not local_path.exists() or not local_path.is_file():
        raise FileNotFoundError(f"Không tìm thấy file ảnh: {local_path}")

    filename = local_path.name
    mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    data = local_path.read_bytes()
    return filename, mime, data


def upload_image(
    image_source: str,
    use_case: str = "inpaint_safe",
    authorization_token: str = "",
    cookie: str = "",
    timeout: int = 120,
):
    filename, mime, image_bytes = _read_image_source_bytes(image_source, timeout=60)

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://sora.chatgpt.com",
        "Referer": "https://sora.chatgpt.com/",
        "User-Agent": "Mozilla/5.0",
    }

    authorization_value = _normalize_authorization_value(authorization_token)
    if authorization_value:
        headers["Authorization"] = authorization_value
    if cookie:
        headers["Cookie"] = cookie

    files = {
        "file": (filename, image_bytes, mime),
    }
    data = {
        "use_case": use_case,
    }

    response = requests.post(
        ENDPOINT,
        headers=headers,
        files=files,
        data=data,
        timeout=timeout,
    )

    body_text = response.text
    try:
        body_json = response.json()
    except Exception:
        body_json = None

    payload = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "request": {
            "endpoint": ENDPOINT,
            "image_source": image_source,
            "filename": filename,
            "mime_type": mime,
            "use_case": use_case,
            "has_authorization": bool(authorization_value),
            "authorization_masked": _mask_authorization(authorization_value),
            "has_cookie": bool(cookie),
        },
        "response": {
            "ok": response.ok,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "json": body_json,
            "text": None if body_json is not None else body_text,
        },
    }

    OUTPUT_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return payload


def main():
    print("=== SORA Upload Image Test ===")
    image_source = (LOCAL_IMAGE_PATH or "").strip().strip('"').strip("'")
    if not image_source:
        image_source = (IMAGE_URL or "").strip()
    if not image_source:
        print("❌ Thiếu nguồn ảnh")
        print("👉 Điền LOCAL_IMAGE_PATH hoặc IMAGE_URL trong file trước khi chạy")
        return

    use_case = (USE_CASE or "inpaint_safe").strip() or "inpaint_safe"
    authorization_token = (AUTHORIZATION_TOKEN or "").strip()
    cookie = (COOKIE or "").strip()

    try:
        result = upload_image(
            image_source=image_source,
            use_case=use_case,
            authorization_token=authorization_token,
            cookie=cookie,
            timeout=int(REQUEST_TIMEOUT or 120),
        )
        status = result["response"]["status_code"]
        ok = result["response"]["ok"]
        print(f"✅ Gửi xong. HTTP {status} | ok={ok}")
        print(f"📄 Đã lưu response vào: {OUTPUT_FILE}")
    except Exception as exc:
        error_payload = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "request": {
                "endpoint": ENDPOINT,
                "image_source": image_source,
                "use_case": use_case,
            },
            "error": str(exc),
        }
        OUTPUT_FILE.write_text(
            json.dumps(error_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"❌ Lỗi: {exc}")
        print(f"📄 Đã lưu lỗi vào: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
