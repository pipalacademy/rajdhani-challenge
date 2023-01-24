from flask import Flask, render_template, abort, jsonify
from jinja2 import Markup
from db import App
import web
import markdown
from tasks import TASKS, Site

app = Flask(__name__)

def markdown_to_html(md):
    return Markup(markdown.markdown(md))

@app.context_processor
def app_context():
    return {
        "datestr": web.datestr,
        "markdown_to_html": markdown_to_html,
    }

@app.route("/")
def home():
    apps = App.find_all()
    internal_users = ["nikochiko", "anandology", "pipalacademy"]
    apps = [app for app in apps if app.name not in internal_users]
    return render_template("index.html", apps=apps)

@app.route("/<name>")
def app_page(name):
    app = App.find(name)
    if not app:
        abort(404)
    return render_template("app.html", app=app, tasks=TASKS)

@app.route("/<name>/deploy", methods=["POST"])
def app_deploy(name):
    app = App.find(name)
    if not app:
        Site(name).create()
        app = App.create(name)

    site = Site(app.name)
    sync_status = site.sync()
    if not sync_status.ok:
        return jsonify({
            "error": "deployment failed to sync",
            "message": sync_status.message
        }), 500
    status = site.get_status()
    app.update_status(status)
    return jsonify(status)

if __name__ == "__main__":
    app.run()
