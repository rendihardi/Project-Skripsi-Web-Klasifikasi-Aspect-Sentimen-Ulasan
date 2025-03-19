from flask import jsonify
import pandas as pd

def get_chart_data():
    try:
        df = pd.read_csv("app/static/data/wondr-dataset.csv")
        aspek_kategori = ["Tampilan", "Autentikasi", "Transaksi"]
        df = df[df["aspek"].isin(aspek_kategori)]

        aspek_counts = df["aspek"].value_counts().to_dict()
        sentimen_counts = df["sentimen"].value_counts().to_dict()
        grouped = df.groupby(["aspek", "sentimen"]).size().unstack(fill_value=0)
        aspek_sentimen_counts = grouped.to_dict(orient="index")

        return jsonify({
            "aspek": aspek_counts,
            "sentimen": sentimen_counts,
            "sentimen_per_aspek": aspek_sentimen_counts
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500