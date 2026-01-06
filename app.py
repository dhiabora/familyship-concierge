import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. 初期設定
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
SHEET_URL = st.secrets["SHEET_URL"]

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. データの読み込み
@st.cache_data
def load_data():
    # スプレッドシートのURLをCSV出力形式に変換
    # 複数のシートがある場合、一番左のシートが読み込まれます
    csv_url = SHEET_URL.split('/edit')[0] + '/export?format=csv'
    df = pd.read_csv(csv_url)
    return df

st.title("👶 ファミリーシップ・コンシェルジュ")

try:
    df = load_data()
    
    # 【確認用】読み込んだデータの行数を表示（あとで消せます）
    st.write(f"現在、{len(df)} 件の講座データを読み込んでいます。")
    if len(df) > 0:
        with st.expander("読み込んだデータの一部を確認する"):
            st.dataframe(df.head()) # 最初の5行を表示

    user_input = st.chat_input("例：夜泣きについて相談したい")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        # AIへの指示（プロンプト）
        # 確実にデータを認識させるため、json形式で渡すように変更
        context_json = df.to_json(orient='records', force_ascii=False)
        
        prompt = f"""
        あなたは子育てサロンの優秀なコンシェルジュです。
        以下の【講座データ(JSON形式)】をもとに、ユーザーの悩みに答えてください。
        
        【講座データ】
        {context_json}
        
        【指示】
        ・ユーザーの悩みに合う講座を最大3つ選んでください。
        ・「講座名」「講師名」「おすすめ理由」「URL」を答えてください。
        ・もし該当するものがなければ、似た分野の講座を提案するか、寄り添うメッセージを伝えてください。
        ・データベースにないデタラメなURLは絶対に作らないでください。
        
        【ユーザーの相談】
        {user_input}
        """

        with st.chat_message("assistant"):
            response = model.generate_content(prompt)
            st.markdown(response.text)

except Exception as e:
    st.error(f"エラーが発生しました: {e}")
