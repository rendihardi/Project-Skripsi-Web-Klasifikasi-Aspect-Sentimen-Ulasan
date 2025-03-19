from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Tambahkan CORS agar bisa diakses dari frontend
app.config["UPLOAD_FOLDER"] = "uploads"
from app import routes  # Import routes setelah inisialisasi app
