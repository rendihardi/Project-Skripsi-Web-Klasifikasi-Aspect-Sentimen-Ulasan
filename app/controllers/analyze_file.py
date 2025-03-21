from flask import request, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
import joblib
import os
from app.preprocessing import Preprocessing

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"csv", "xlsx"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Load model aspek dan sentimen
aspek_models = {
    "Tampilan": joblib.load("app/models/model_aspek_tampilan.pkl"),
    "Autentikasi": joblib.load("app/models/model_aspek_autentikasi.pkl"),
    "Transaksi": joblib.load("app/models/model_aspek_transaksi.pkl"),
}

sentimen_models = {
    "Tampilan": joblib.load("app/models/model_sentimen_tampilan.pkl"),
    "Autentikasi": joblib.load("app/models/model_sentimen_autentikasi.pkl"),
    "Transaksi": joblib.load("app/models/model_sentimen_transaksi.pkl"),
}

def api_analyze_file(request):
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        filename = secure_filename(file.filename)
        ext = filename.rsplit(".", 1)[1].lower()
        if not allowed_file(filename):
            return jsonify({"error": "Invalid file type. Only CSV/XLSX allowed."}), 400
        if ext == "csv":
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        if "review" not in df.columns:
            return jsonify({"error": "File must contain a 'review' column"}), 400
        results = []
        preprocessor = Preprocessing()
        for review in df["review"].dropna():
            processed_text = preprocessor.preprocess_text(review)
            detected_aspects = []

            for aspek, model_dict in aspek_models.items():
                vectorizer = model_dict.get(f"vectorizer_{aspek.lower()}")
                model = model_dict.get(f"stacking_clf_{aspek.lower()}")

                if vectorizer and model:
                    text_vectorized = vectorizer.transform([processed_text])
                    aspek_pred = model.predict(text_vectorized)[0]

                    if aspek_pred == 0:
                        sent_dict = sentimen_models.get(aspek, {})
                        sent_vectorizer = sent_dict.get(f"vectorizer_sen_{aspek.lower()}")
                        sent_model = sent_dict.get(f"stacking_clf_sen_{aspek.lower()}")

                        if sent_vectorizer and sent_model:
                            text_vectorized_sent = sent_vectorizer.transform([processed_text])
                            sent_pred = sent_model.predict(text_vectorized_sent)[0]
                            sent_label = "Positive" if sent_pred == 0 else "Negative"

                            detected_aspects.append({"name": aspek, "sentimen": sent_label})

            results.append({"review": review, "aspects": detected_aspects if detected_aspects else "Tidak ada aspek"})

        return jsonify({"results": results})

    except Exception as e:
        print("Error di API Analyze File:", str(e))  # Debugging di terminal
        return jsonify({"error": str(e)}), 500
