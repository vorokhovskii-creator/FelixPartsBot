release: python felix_hub/backend/init_db.py
web: gunicorn -w 2 -b 0.0.0.0:$PORT felix_hub.backend.app:app
worker: python -m felix_hub.bot.bot
