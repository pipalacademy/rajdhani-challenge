import web
import datetime

db = web.database("sqlite:///rajdhani.db")

def get_apps():
    apps = db.select("app", order="score desc")
    return [process_app(app) for app in apps]

def process_app(app):
    app.created = parse_timestamp(app.created)
    app.last_updated = parse_timestamp(app.last_updated)
    return app

def parse_timestamp(timestamp):
    return datetime.datetime.fromisoformat(timestamp)
