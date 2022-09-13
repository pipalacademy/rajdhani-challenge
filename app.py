from flask import Flask, render_template
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

if __name__ == "__main__":
    app.run()
