import re
import string
import os
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Pastikan komponen NLTK sudah diunduh
nltk.download('stopwords')
nltk.download('punkt_tab')

class Preprocessing:

    def __init__(self):
        # Membaca kamus kata baku
        try:
            self.kamus_baku = pd.read_excel("app/models/kamuskatabaku.xlsx")
            self.baku_dict = dict(zip(self.kamus_baku['tidak_baku'], self.kamus_baku['kata_baku']))
        except Exception:
            self.baku_dict = {}

        try:
            kata_baru_df = pd.read_csv("app/models/normalisasinew.csv")
            if "tidak_baku" in kata_baru_df.columns and "kata_baku" in kata_baru_df.columns:
                self.kata_baru_dict = dict(zip(kata_baru_df['tidak_baku'], kata_baru_df['kata_baku']))
                self.baku_dict.update(self.kata_baru_dict)
        except Exception:
            pass

        # Stopwords list
        self.stopwords = set(stopwords.words('indonesian'))
        words_to_keep = {'kurang', 'tidak', 'masih', 'belum', 'baik', 'sangat', 'lama', 'sering', 'tanpa', 'enggak', 'lebih', 'bisa'}
        words_to_remove = {'nya', 'ya', 'by', 'aplikasi', 'aplikasinya', 'wondr', 'bni'}

        self.stopwords.difference_update(words_to_keep)
        self.stopwords.update(words_to_remove)

        # Stemming
        factory = StemmerFactory()
        self.stemmer = factory.create_stemmer()
        self.exception_words = {"perbaikan", "diperbaiki", "tampilan", "layanan", "menarik", "gangguan"}

    def clean_text(self, text):
        text = text.lower()

        text = re.sub(r"[^\x00-\x7F]+", "", text)  
        text = re.sub(r"[^\w\s]", " ", text) 
        text = re.sub(r"\s+", " ", text).strip()
        
        return text.strip()

    def normalize_text(self, text):
        words = text.split()
        normalized_words = [self.baku_dict.get(word, word) for word in words]
        return " ".join(normalized_words)

    def remove_stopwords(self, text):
        words = text.split()
        filtered_words = [word for word in words if word not in self.stopwords]
        return " ".join(filtered_words)

    def tokenize(self, text):
        return word_tokenize(text)

    def stemming(self, tokens):
        return [token if token in self.exception_words else self.stemmer.stem(token) for token in tokens]

    def preprocess_text(self, text):
        text = self.clean_text(text)
        text = self.normalize_text(text)
        text = self.remove_stopwords(text)
        tokens = self.tokenize(text)
        stemmed_tokens = self.stemming(tokens)
        return " ".join(stemmed_tokens)
