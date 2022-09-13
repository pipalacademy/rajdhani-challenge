from flask import Flask, render_template, abort
import db
import web

app = Flask(__name__)

@app.context_processor
def app_context():
    return {
        "datestr": web.datestr
    }

@app.route("/")
def home():
    apps = db.get_apps()
    return render_template("index.html", apps=apps)

@app.route("/<name>")
def app_page(name):
    app = db.get_app(name)
    if not app:
        abort(404)
    return render_template("app.html", app=app)

if __name__ == "__main__":
    app.run()
