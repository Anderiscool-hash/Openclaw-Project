# MiniMax Backup Agent

Standalone backup agent scaffold so it can be deployed anytime.

## Setup
```bash
cd minimax_backup_agent
cp .env.example .env
# add MINIMAX_API_KEY
pip install -r requirements.txt
```

## Test
```bash
./run.sh "Say backup online"
```

## Notes
- Keep key in `.env` only.
- Do not commit `.env`.
