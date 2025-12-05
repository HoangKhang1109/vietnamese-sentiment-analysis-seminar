# model.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
import re

class SentimentAnalyzer:
    def __init__(self):
        # Model PhoBERT
        model_name = "wonrax/phobert-base-vietnamese-sentiment"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=self.model,
            tokenizer=self.tokenizer,
            return_all_scores=False
        )

        # --- TỪ ĐIỂN CHUẨN HÓA, VIẾT TẮT ---
        self.teencode_dict = {
            "mik": "mình", "mk": "mình",
            "ko": "không", "k": "không", "khong": "không",
            "dc": "được", "duoc": "được",
            "bt": "bình thường", "binh thuong": "bình thường",
            "rat": "rất",
            "tot": "tốt",
            "vui": "vui", 
            "buon": "buồn",
            "met": "mệt",
            "chan": "chán",
            "thich": "thích",
            "iu": "yêu", "yeu": "yêu",
            "hnay": "hôm nay", "hom nay": "hôm nay",
            "wa": "quá", "qua": "quá",
            "do": "dở",
            "oke": "ok",
            "thk": "thích",
            "ghet": "ghét"
        }

    def normalize_text(self, text: str):
        text = text.lower()        
        words = text.split()
        normalized_words = []
        for word in words:
            # Nếu từ có trong từ điển thay thế -> đổi sang tiếng Việt chuẩn
            if word in self.teencode_dict:
                normalized_words.append(self.teencode_dict[word])
            else:
                normalized_words.append(word)       
        return " ".join(normalized_words)

    def predict(self, text: str):
        # Tiền xử lý (Thêm dấu/sửa lỗi)
        clean_text = self.normalize_text(text) 
        # Đưa vào model
        result = self.sentiment_pipeline(clean_text)[0]
        label = result['label']
        score = result['score']  
        mapping = {
            'POS': 'POSITIVE',
            'NEG': 'NEGATIVE',
            'NEU': 'NEUTRAL',
            'positive': 'POSITIVE',
            'negative': 'NEGATIVE',
            'neutral': 'NEUTRAL'
        }
        final_label = mapping.get(label, "NEUTRAL")
        if score < 0.5:
            final_label = "NEUTRAL"
            
        return {
            "text": text,        
            "processed_text": clean_text,
            "sentiment": final_label,
            "confidence": round(score, 4)
        }

analyzer = SentimentAnalyzer()