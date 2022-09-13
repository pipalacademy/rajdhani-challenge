from flask import Flask, render_template, abort
from db import App
import web
from tasks import TASKS

app = Flask(__name__)

@app.context_processor
def app_context():
    return {
        "datestr": web.datestr
    }

@app.route("/")
def home():
    apps = App.find_all()
    return render_template("index.html", apps=apps)

@app.route("/<name>")
def app_page(name):
    app = App.find(name)
    if not app:
        abort(404)
    return render_template("app.html", app=app, tasks=TASKS.values())

if __name__ == "__main__":
    app.run()
