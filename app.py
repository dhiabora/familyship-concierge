import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. 初期設定
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
SHEET_URL = st.secrets["SHEET_URL"]

# Geminiの設定（1.5-flashが無料枠で最も安定しています）
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. データの読み込み
@st.cache_data
def load_data():
    try:
        # 共有URLからCSVエクスポート用URLを作成
        # gid=0を指定することで、一番左のシートを強制的に読み込みます
        base_url = SHEET_URL.split('/edit')[0]
        csv_url = f"{base_url}/export?format=csv&gid=0"
        df = pd.read_csv(csv_url)
        # 空白の行や列を削除
        df = df.dropna(how='all').dropna(axis=1, how='all')
        return df
    except Exception as e:
        st.error(f"データの読み込みに失敗しました: {e}")
        return pd.DataFrame()

# アプリの画面構成
st.set_page_config(page_title="ファミリーシップ・コンシェルジュ", page_icon="👶")
st.title("👶 ファミリーシップ・コンシェルジュ")

df = load_data()

# 【デバッグ用】読み込み状況を確認（動作確認ができたら削除してOK）
st.sidebar.write(f"読み込み件数: {len(df)} 件")
if not df.empty:
    with st.sidebar.expander("読み込んだデータの中身を確認"):
        st.write(df.head())

# メインチャット
user_input = st.chat_input("例：イヤイヤ期の対応を知りたい")

if user_input:
    if df.empty:
        st.warning("講座データが読み込めていません。スプレッドシートの共有設定やURLを確認してください。")
    else:
        with st.chat_message("user"):
            st.markdown(user_input)

        # 講座リストをAIに渡す（列名を明示）
        context = df.to_string(index=False)
        
        prompt = f"""
        あなたは子育てサロン「ファミリーシップ」のコンシェルジュです。
        以下の【講座リスト】をもとに、ユーザーの悩みに答えてください。
        
        【講座リスト】
        {context}
        
        【ルール】
        ・「講座タイトル」「講師名」「対象年齢」「内容」「該当URL」の情報を活用してください。
        ・最適な講座を最大3つ選んで、そのURLを必ず提示してください。
        ・優しく温かい言葉で回答してください。
        ・リストにない情報は「申し訳ありませんが、該当する講座が見つかりませんでした」と答えてください。
        
        【相談内容】
        {user_input}
        """

        with st.chat_message("assistant"):
            with st.spinner("考え中..."):
                response = model.generate_content(prompt)
                st.markdown(response.text)
