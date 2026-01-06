import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. 初期設定（セキュリティのためAPIキーはStreamlitの設定から読み込みます）
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
SHEET_URL = st.secrets["SHEET_URL"] # スプレッドシートのCSVエクスポートURL

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. データの読み込み
@st.cache_data
def load_data():
    # スプレッドシートをCSV形式で読み込みます
    url = SHEET_URL.replace('/edit?usp=sharing', '/export?format=csv')
    df = pd.read_csv(url)
    return df

# アプリのタイトル
st.title("育児講座コンシェルジュ")
st.write("あなたのお悩みにぴったりの講座をご案内します。")

try:
    df = load_data()
    
    # ユーザーの入力
    user_input = st.chat_input("例：1歳の夜泣きについて知りたい")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        # AIへの指示（プロンプト）の作成
        # ナレッジを保護しつつ、適切な講座を提案させるための魔法の文章です
        context = df.to_string(index=False)
        prompt = f"""
        あなたは子育てサロンの優しく頼れるコンシェルジュです。
        以下の【講座データベース】の内容をもとに、ユーザーの悩みに答えてください。
        
        【ルール】
        ・おすすめの講座を最大3つ提案してください。
        ・回答には「講座名」「講師名」「なぜおすすめか」「視聴URL」を必ず含めてください。
        ・データベースにない情報は答えないでください。
        ・データベースの生データをそのまま出力せず、お母さんに寄り添う言葉で回答してください。
        
        【講座データベース】
        {context}
        
        【ユーザーの質問】
        {user_input}
        """

        with st.chat_message("assistant"):
            response = model.generate_content(prompt)
            st.markdown(response.text)

except Exception as e:
    st.error("データの読み込みに失敗しました。URLや設定を確認してください。")
