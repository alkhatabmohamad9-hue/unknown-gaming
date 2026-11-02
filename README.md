# 𝑈𝑁𝐾𝑁𝑂𝑊𝑁

Starter project for a Telegram gaming bot.

## Included
- Telegram bot menu and callback buttons
- SQLite user registration and virtual points
- Referral links (5 virtual points for a successful new referral)
- Basic admin statistics via `/admin`
- Render Background Worker configuration

## Run locally
1. Install Python 3.11 or newer.
2. Run `pip install -r requirements.txt`.
3. Set environment variables `BOT_TOKEN` and `ADMIN_ID`.
4. Run `python bot.py`.

Never commit your real bot token. Set it as a secret environment variable in Render.

## Deploy on Render
Create a Background Worker from this repository. Build command:
`pip install -r requirements.txt`

Start command:
`python bot.py`

Set environment variables:
- `BOT_TOKEN`: your Telegram bot token
- `ADMIN_ID`: your numeric Telegram user ID

SQLite is suitable only for an initial test. For a production deployment, use persistent storage or migrate to PostgreSQL. Render's filesystem may be ephemeral unless a persistent disk is configured.

## Safety
This starter uses virtual, non-redeemable points only. No real-money deposits, withdrawals, or wagering are implemented.
