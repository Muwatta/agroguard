from flask import Flask, render_template, jsonify
import os
from services.detection import get_pest_events

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), "static/captures")

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/api/events")
def events():
    return jsonify(get_pest_events())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)