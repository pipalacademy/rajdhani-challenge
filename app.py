from flask import Flask, render_template, abort, jsonify
from db import App
import web
from tasks import TASKS, Site

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

@app.route("/<name>/deploy", methods=["POST"])
def app_deploy(name):
    app = App.find(name)
    if not app:
        abort(404)
    site = Site(app.name)
    status = site.get_status()
    app.update_status(status)
    return jsonify(status)

if __name__ == "__main__":
    app.run()
