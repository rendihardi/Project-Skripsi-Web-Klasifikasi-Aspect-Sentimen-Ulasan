from flask import Blueprint, render_template, request, jsonify, send_file
from app.controllers.analyze_text import analyze_text_api
from app.controllers.analyze_file import api_analyze_file
from app.controllers.chart_data import get_chart_data
import os

routes = Blueprint("routes", __name__)

@routes.route("/")
def home():
    return render_template("home.html")

@routes.route("/analyze-text", methods=["GET"])
def analyze_text():
    return render_template("analyze_text.html")

@routes.route("/analyze-file", methods=["GET"])
def analyze_file():
    return render_template("analyze_file.html")

@routes.route("/chart-data", methods=["GET"])
def chart_data():
    return get_chart_data()

@routes.route("/api/analyze-text", methods=["POST"])
def api_analyze_text():
    return analyze_text_api(request)

@routes.route("/api/analyze-file", methods=["POST"])
def api_analyze_file_route():
    return api_analyze_file(request)

# Route untuk download hasil analisis CSV
@routes.route("/download-csv")
def download_csv():
    file_path = "static/outputs/hasil_analisis.csv"

    try:
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}", 500
