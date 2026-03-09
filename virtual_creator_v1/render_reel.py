#!/usr/bin/env python3
import time
from pathlib import Path
from json2video_client import load_env, create_movie, get_movie, save_json

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs'
OUT.mkdir(exist_ok=True)


def build_payload():
    # Minimal reel payload (9:16) with text + voice + bg color.
    # Adjust according to JSON2Video docs/examples as needed.
    script = "If your mornings feel chaotic, do this 3-step reset. Water and sunlight. Ten minutes movement. One priority task."

    return {
        "comment": "Virtual Creator Reel #1",
        "resolution": "1080x1920",
        "quality": "high",
        "scenes": [
            {
                "elements": [
                    {
                        "type": "shape",
                        "shape": "rectangle",
                        "x": 0,
                        "y": 0,
                        "width": 1080,
                        "height": 1920,
                        "fill": "#0f172a"
                    },
                    {
                        "type": "text",
                        "text": "3-Step Morning Reset",
                        "fontSize": 72,
                        "color": "#ffffff",
                        "x": 540,
                        "y": 280,
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "1) Water + sunlight\\n2) 10-min movement\\n3) One priority task",
                        "fontSize": 44,
                        "color": "#cbd5e1",
                        "x": 540,
                        "y": 760,
                        "align": "center"
                    },
                    {
                        "type": "voice",
                        "text": script,
                        "voice": "en-US-Neural2-F"
                    }
                ]
            }
        ]
    }


def main():
    load_env()
    payload = build_payload()
    res = create_movie(payload)
    save_json(OUT / 'create_response.json', res)

    movie_id = res.get('movie') or res.get('id') or res.get('movieId')
    if not movie_id:
        print('Created request, but no movie id found. Check outputs/create_response.json')
        return

    print('movie_id:', movie_id)
    for _ in range(40):
        st = get_movie(str(movie_id))
        save_json(OUT / 'status_response.json', st)
        status = (st.get('status') or '').lower()
        print('status:', status or st)
        if status in {'done', 'completed', 'ready'}:
            print('Rendered ✅ check output URL in status_response.json')
            return
        if status in {'failed', 'error'}:
            print('Render failed ❌ check status_response.json')
            return
        time.sleep(5)

    print('Timed out waiting for render; check status_response.json')


if __name__ == '__main__':
    main()
