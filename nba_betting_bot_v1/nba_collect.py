#!/usr/bin/env python3
import os, json, requests
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'odds_raw.json'


def load_env():
    env = ROOT / '.env'
    if env.exists():
        for line in env.read_text().splitlines():
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())


def main():
    load_env()
    key = os.getenv('ODDS_API_KEY', '')
    base = os.getenv('ODDS_API_BASE', 'https://api.the-odds-api.com/v4').rstrip('/')
    sport = os.getenv('SPORT', 'basketball_nba')
    regions = os.getenv('REGIONS', 'us')
    markets = os.getenv('MARKETS', 'h2h,spreads,totals')
    odds_format = os.getenv('ODDS_FORMAT', 'american')
    date_format = os.getenv('DATE_FORMAT', 'iso')

    if not key:
        raise SystemExit('Missing ODDS_API_KEY in .env')

    url = f"{base}/sports/{sport}/odds"
    params = {
        'apiKey': key,
        'regions': regions,
        'markets': markets,
        'oddsFormat': odds_format,
        'dateFormat': date_format,
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()

    RAW.write_text(json.dumps(r.json(), indent=2))
    print(f'Wrote odds -> {RAW}')


if __name__ == '__main__':
    main()
