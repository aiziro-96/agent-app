from flask import Flask, render_template, request
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import os
import sqlite3
from datetime import datetime

load_dotenv()

app = Flask(__name__)

key = os.getenv("LANGUAGE_KEY")
endpoint = os.getenv("LANGUAGE_ENDPOINT")

credential = AzureKeyCredential(key)

client = TextAnalyticsClient(
    endpoint=endpoint,
    credential=credential
)

def init_db():
    conn = sqlite3.connect("history.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS histories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            study TEXT,
            sentiment TEXT,
            advice TEXT,
            todo TEXT,
            memo TEXT,
            created_at TEXT
        )
    """)
    
    try:
        c.execute("ALTER TABLE histories ADD COLUMN memo TEXT")
    except sqlite3.OperationalError:
        pass
    
    conn.commit()
    conn.close()

init_db()

@app.route("/", methods=["GET", "POST"])
def home():
    
    result = ""
    histories = []
    
    if request.method == "POST":
        study = request.form["study"]
        memo = request.form["memo"]
        response = client.analyze_sentiment(
            documents=[study]
        )[0]

        sentiment = response.sentiment
        
        key_phrase_response = client.extract_key_phrases(
            documents=[study]
        )[0]

        filtered_phrases = []

        for phrase in key_phrase_response.key_phrases:

            if len(phrase) >= 2:
                filtered_phrases.append(phrase)

        key_phrases = ", ".join(filtered_phrases[:3])
        
        if sentiment == "positive":
            sentiment_jp = "前向き"
            advice = "順調に学習を進められています！"
            todo = "明日は少し難しめの問題に挑戦してみましょう。"

        elif sentiment == "negative":
            sentiment_jp = "悩み・疲れあり"
            advice = "難しい内容にも挑戦できています。少しずつ復習していきましょう！"
            todo = "明日は苦手な部分を1つだけ選んで、15分復習しましょう。"

        else:
            sentiment_jp = "安定"
            advice = "安定して学習を継続できています！"
            todo = "明日は今日の内容を3問だけ復習してみましょう。"

        negative_words = [
            "難しい",
            "苦手",
            "疲れた",
            "焦った",
            "混乱"
        ]

        for word in negative_words:
            if word in study:
                sentiment_jp = "悩み・疲れあり"
                advice = "難しい内容にも挑戦できています。少しずつ復習していきましょう！"
                todo = "明日は苦手な部分を1つだけ選んで、15分復習しましょう。"

 
        result = f"""
        【学習レポート】

        ■ 学習内容
        {study}

        ■ 感情分析
        {sentiment_jp}
        
        ■ AIから提案された明日のTODO
        {todo}
        
        ■ 明日やることメモ
        {memo}

        ■ AIコメント
        {advice}
        """
        
        conn = sqlite3.connect("history.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO histories (
                study, 
                sentiment, 
                advice, 
                todo, 
                memo,
                created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            study,
            sentiment_jp,
            advice,
            todo,
            memo,
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))
        conn.commit()
        conn.close()
        
        conn = sqlite3.connect("history.db")
        c = conn.cursor()
        c.execute("""
            SELECT study, sentiment, advice, todo, memo, created_at
            FROM histories
            ORDER BY id DESC
            LIMIT 5
        """)
        histories = c.fetchall()
        conn.close()
    return render_template("index.html", result=result, histories=histories)

if __name__ == "__main__":
    app.run(debug=True)