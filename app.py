from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    
    result = ""
    
    if request.method == "POST":
        study = request.form["study"]
        trouble = request.form["trouble"]
        result = f"""
        【学習レポート】

        ■ 今日の学習
        {study}

        ■ 現在の課題
        {trouble}

        ■ 優先度
        ネットワーク分野の復習を優先するのがおすすめです。

        ■ 明日のアクション
        ・30分だけ復習
        ・関連問題を3問解く

        ■ AIコメント
        継続して取り組めていて素晴らしいです！
        """
        
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)