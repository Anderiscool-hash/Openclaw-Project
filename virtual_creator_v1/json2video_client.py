#!/usr/bin/env python3
import os, json, requests
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_env():
    env = ROOT / '.env'
    if env.exists():
        for line in env.read_text().splitlines():
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())


def api_headers():
    key = os.getenv('JSON2VIDEO_API_KEY', '')
    if not key:
        raise RuntimeError('Missing JSON2VIDEO_API_KEY')
    return {'x-api-key': key, 'Content-Type': 'application/json'}


def base_url():
    return os.getenv('JSON2VIDEO_BASE_URL', 'https://api.json2video.com/v2').rstrip('/')


def create_movie(payload: dict):
    url = f"{base_url()}/movies"
    r = requests.post(url, headers=api_headers(), json=payload, timeout=60)
    r.raise_for_status()
    return r.json()


def get_movie(movie_id: str):
    url = f"{base_url()}/movies/{movie_id}"
    r = requests.get(url, headers=api_headers(), timeout=60)
    r.raise_for_status()
    return r.json()


def save_json(path: Path, data: dict):
    path.write_text(json.dumps(data, indent=2))
