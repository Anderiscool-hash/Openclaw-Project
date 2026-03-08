# NBA Betting Bot v1

Builds best-value picks from odds markets (moneyline, spreads, totals, and player props when available from provider).

## Setup
```bash
cd nba_betting_bot_v1
cp .env.example .env
# add ODDS_API_KEY
pip install -r requirements.txt
```

## Run
```bash
./run_nba_bot.sh
```

Outputs:
- `odds_raw.json`
- `modeled_edges.csv`
- `nba_picks_today.csv`
- `nba_picks_today.txt`

## Notes
- v1 uses market-implied normalization as fair-prob baseline (de-vig style).
- Add your own model/features in v2 (injuries, rest, pace, matchup priors).
- No guaranteed wins; manage bankroll carefully.
