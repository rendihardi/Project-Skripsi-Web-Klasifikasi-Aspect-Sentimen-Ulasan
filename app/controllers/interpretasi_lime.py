from flask import jsonify
import joblib
from lime.lime_text import LimeTextExplainer
from sklearn.pipeline import make_pipeline
from app.preprocessing import Preprocessing

# Load model aspek
aspek_models = {
    "Tampilan": joblib.load("app/models/model_aspek_tampilan.pkl"),
    "Autentikasi": joblib.load("app/models/model_aspek_autentikasi.pkl"),
    "Transaksi": joblib.load("app/models/model_aspek_transaksi.pkl"),
}

# Load model sentimen
sentimen_models = {
    "Tampilan": joblib.load("app/models/model_sentimen_tampilan.pkl"),
    "Autentikasi": joblib.load("app/models/model_sentimen_autentikasi.pkl"),
    "Transaksi": joblib.load("app/models/model_sentimen_transaksi.pkl"),
}

def modify_lime_html(html):
    """Modifikasi HTML dari LIME supaya layout sejajar horizontal."""
    return html.replace(
        '<body>',
        '<body><div style="display: flex; align-items: flex-start; gap: 20px;">'
    ).replace(
        '</body>',
        '</div></body>'
    )

def interpretasi_lime_api(request):
    try:
        data = request.get_json()
        if not data or "review" not in data:
            return jsonify({"error": "No text provided"}), 400

        review = data["review"]

        # Preprocessing text
        preprocessor = Preprocessing()
        processed_text = preprocessor.preprocess_text(review)

        explanations = []

        for aspek, model_dict in aspek_models.items():
            vectorizer_aspek = model_dict.get(f"vectorizer_{aspek.lower()}")
            model_aspek = model_dict.get(f"stacking_clf_{aspek.lower()}")

            if vectorizer_aspek and model_aspek:
                text_vectorized_aspek = vectorizer_aspek.transform([processed_text])
                aspek_pred = model_aspek.predict(text_vectorized_aspek)[0]

                if aspek_pred == 0:  # 0 berarti aspek terdeteksi
                    # Interpretasi Aspek
                    pipeline_aspek = make_pipeline(vectorizer_aspek, model_aspek)
                    explainer_aspek = LimeTextExplainer(class_names=[aspek, f"Non-{aspek}"])
                    exp_aspek = explainer_aspek.explain_instance(
                        processed_text,
                        pipeline_aspek.predict_proba,
                        num_features=5
                    )
                    aspek_html = modify_lime_html(exp_aspek.as_html())

                    # Interpretasi Sentimen
                    sentimen_dict = sentimen_models.get(aspek)
                    if sentimen_dict:
                        vectorizer_sentimen = sentimen_dict.get(f"vectorizer_sen_{aspek.lower()}")
                        model_sentimen = sentimen_dict.get(f"stacking_clf_sen_{aspek.lower()}")

                        if vectorizer_sentimen and model_sentimen:
                            text_vectorized_sentimen = vectorizer_sentimen.transform([processed_text])
                            sentimen_pred = model_sentimen.predict(text_vectorized_sentimen)[0]
                            sentimen_label = "Positive" if sentimen_pred == 0 else "Negative"

                            pipeline_sentimen = make_pipeline(vectorizer_sentimen, model_sentimen)
                            explainer_sentimen = LimeTextExplainer(class_names=["Positive", "Negative"])
                            exp_sentimen = explainer_sentimen.explain_instance(
                                processed_text,
                                pipeline_sentimen.predict_proba,
                                num_features=5
                            )
                            sentimen_html = modify_lime_html(exp_sentimen.as_html())

                            explanations.append({
                                "aspek": aspek,
                                "sentimen": sentimen_label,
                                "lime_aspek_html": aspek_html,
                                "lime_sentimen_html": sentimen_html
                            })

        if not explanations:
            return jsonify({"message": "No aspects detected"}), 200

        return jsonify({"interpretations": explanations})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
