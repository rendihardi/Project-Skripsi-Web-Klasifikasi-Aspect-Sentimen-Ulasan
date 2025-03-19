from flask import jsonify
import joblib
from app.preprocessing import Preprocessing

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

def analyze_text_api(request):
    try:
        data = request.get_json()
        if not data or "review" not in data:
            return jsonify({"error": "No text provided"}), 400

        review = data["review"]
        preprocessor = Preprocessing()
        processed_text = preprocessor.preprocess_text(review)

        detected_aspects = []
        for aspek, model_dict in aspek_models.items():
            vectorizer = model_dict.get(f"vectorizer_{aspek.lower()}")
            model = model_dict.get(f"stacking_clf_{aspek.lower()}")

            if vectorizer and model:
                text_vectorized = vectorizer.transform([processed_text])
                aspek_pred = model.predict(text_vectorized)[0]

                if aspek_pred == 0:
                    sent_dict = sentimen_models[aspek]
                    sent_vectorizer = sent_dict.get(f"vectorizer_sen_{aspek.lower()}")
                    sent_model = sent_dict.get(f"stacking_clf_sen_{aspek.lower()}")

                    if sent_vectorizer and sent_model:
                        text_vectorized_sent = sent_vectorizer.transform([processed_text])
                        sent_pred = sent_model.predict(text_vectorized_sent)[0]
                        sent_label = "Positive" if sent_pred == 0 else "Negative"

                        detected_aspects.append({"name": aspek, "sentimen": sent_label})

        return jsonify({"aspects": detected_aspects})
    except Exception as e:
        return jsonify({"error": str(e)}), 500