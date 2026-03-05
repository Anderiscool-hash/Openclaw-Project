# Dominican Lottery Data Quality Notes

## Scope
- Source: https://www.conectate.com.do/loterias/
- Games covered (13): Gana Mas, Loteria Nacional, Quiniela Leidsa, Quiniela Real, Quiniela Loteka, La Primera Dia, La Primera Noche, La Suerte MD, La Suerte 6PM, Anguila 10:00 AM, Anguila 1:00 PM, Anguila 6:00 PM, Anguila 9:00 PM.
- Files generated:
  - `dominican_lottery_data.csv`
  - `dominican_lottery_top10_predictions.csv`

## Method Summary
- Direct API endpoint was protected for non-browser traffic.
- Data was extracted from historical cards rendered in page HTML (`game-block` + `game-scores`).
- Multi-page history was traversed using `?date=dd-mm-yyyy` backfill.

## Known Limitations
- Some games show shallower history than others on public pages.
- `extras` and `jackpot` fields are mostly blank for these game pages.
- Date/year rollover is inferred from page context and history traversal.
- Predictions are baseline probabilities (frequency + recency decay), not guaranteed outcomes.

## Coverage Snapshot
- Total rows: 5,610
- Games: 13
- Approximate date coverage by game varies (best coverage in Leidsa/Real; shallower in some National pages).

## Model Note
- Top-10 probabilities are computed per game from weighted historical frequency.
- Weighting uses exponential recency decay to favor recent draws.
