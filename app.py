import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. 初期設定（Secretsから安全に読み込みます）
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
SHEET_URL = st.secrets["SHEET_URL"]

# Gemini 2.5 Flashの設定
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. データの読み込み（キャッシュ機能で高速化）
@st.cache_data
def load_data():
    # スプレッドシートのURLをCSV出力形式に変換して読み込み
    csv_url = SHEET_URL.split('/edit')[0] + '/export?format=csv'
    return pd.read_csv(csv_url)

# アプリの画面構成
st.set_page_config(page_title="ねんねママのファミリーシップ・コンシェルジュ", page_icon="👶")
st.title("👶 ねんねママのファミリーシップ・コンシェルジュ")
st.info("全講座から、あなたにぴったりの内容をご提案します。")

try:
    df = load_data()
    
    user_input = st.chat_input("例：1歳の夜泣きについて相談したい")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        # 講座リストをテキストに変換してAIに渡す
        context = df.to_string(index=False)
        
        # AIへの指示（システムプロンプト）
        prompt = f"""
        あなたは「ねんねママのファミリーシップ」の優秀なコンシェルジュです。
        以下の【講座リスト】をもとに、ユーザーの悩みに答えてください。
        
        【ルール】
        ・最適な講座を最大3つピックアップしてください。
        ・「講座名」「講師名」「おすすめする理由」「視聴URL」をセットで伝えてください。
        ・温かく、お母さんの心に寄り添う丁寧な言葉遣いで回答してください。
        ・リストにないURLや情報は絶対に作り出さないでください。
        
        【講座リスト】
        {context}
        
        【ユーザーの相談】
        {user_input}
        """

        with st.chat_message("assistant"):
            response = model.generate_content(prompt)
            st.markdown(response.text)

except Exception as e:
    st.error("データの読み込み中にエラーが発生しました。設定（Secrets）のURLやAPIキーを確認してください。")
