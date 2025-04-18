import json
from config import DATA_FILE

def load_news_articles():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)
