from preprocessing import Preprocessing

# Inisialisasi objek preprocessing
preprocessor = Preprocessing()

# Contoh teks yang akan diuji
sample_text = "Tampilanya bagus, tapi transaksi lama, daftar akun juga susah"

# Jalankan preprocessing
processed_text = preprocessor.preprocess_text(sample_text)

# Cetak hasil preprocessing
print("\n===== HASIL PREPROCESSING =====")
print(f"Original Text: {sample_text}")
print(f"Processed Text: {processed_text}")
