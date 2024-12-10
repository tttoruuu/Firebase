import streamlit as st
import os
from firebase_admin import credentials, initialize_app, firestore, auth
import firebase_admin
from dotenv import load_dotenv

# Firebaseの初期化
def initialize_firebase():
    # Firebaseが初期化されていない場合のみ実行
    if not firebase_admin._apps:
        load_dotenv()  # .env ファイルを読み込む

        # 環境変数からFirebaseキーのパスを取得
        firebase_key_path = os.getenv("FIREBASE_LOCAL_KEY")
        if firebase_key_path and os.path.exists(firebase_key_path):
            # ローカル環境
            cred = credentials.Certificate(firebase_key_path)
        elif os.path.exists(".streamlit/secrets.toml"):
            # デプロイ環境
            firebase_secrets = dict(st.secrets["firebase"])
            cred = credentials.Certificate(firebase_secrets)
        else:
            raise FileNotFoundError("Firebaseのキー情報が見つかりません。secrets.toml または .env を設定してください。")

        initialize_app(cred)

    return firestore.client()


# Firestoreクライアントを取得
db = initialize_firebase()

# ユーザー登録
def register_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        st.success(f"新しいユーザーが作成されました: {user.uid}")
        return user
    except Exception as e:
        st.error(f"ユーザー登録中にエラーが発生しました: {e}")

# ログイン（仮のセッション管理）
def login_user(email):
    try:
        user = auth.get_user_by_email(email)
        st.session_state["user"] = {"email": user.email, "uid": user.uid}
        st.success(f"ようこそ、{email} さん！")
        return True
    except Exception as e:
        st.error(f"ログイン中にエラーが発生しました: {e}")
        return False

# Firestoreにデータを保存
def save_user_data(uid, mbti, habit_goal):
    try:
        user_ref = db.collection("users").document(uid)
        user_ref.set({"mbti": mbti, "habit_goal": habit_goal})
        st.success("データが保存されました！")
    except Exception as e:
        st.error(f"データ保存中にエラーが発生しました: {e}")

# ユーザー情報入力/確認ページ
def user_dashboard():
    st.title("ユーザー情報の確認")

    uid = st.session_state["user"]["uid"]
    user_ref = db.collection("users").document(uid)
    user_data = user_ref.get().to_dict()

    # データベースに既存データがあるか確認
    if user_data and "mbti" in user_data and "habit_goal" in user_data:
        st.write("以下の情報がデータベースに保存されています:")
        st.write(f"**MBTI**: {user_data['mbti']}")
        st.write(f"**習慣化したいこと**: {user_data['habit_goal']}")

        # 「これでOK」または「やり直す」ボタン
        col1, col2 = st.columns(2)
        with col1:
            if st.button("これでOK"):
                st.success("次のページに進みます。")
                st.stop()

        with col2:
            if st.button("やり直す"):
                st.warning("既存のデータをキャンセルし、再入力します。")
                user_ref.delete()  # 既存データを削除
                st.session_state["rerun"] = not st.session_state.get("rerun", False)

    else:
        st.write("データがまだ存在しません。以下に入力してください。")
        # 新しいデータの入力フォーム
        mbti = st.selectbox("あなたのMBTIを選択してください", ["ENFP", "INTJ", "INFJ", "ENTP", "その他"])
        habit_goal = st.text_input("習慣化したいことを入力してください")

        if st.button("保存"):
            save_user_data(uid, mbti, habit_goal)
            st.session_state["rerun"] = not st.session_state.get("rerun", False)

# メインアプリケーション
def app():
    st.title("クロノクエスト")

    # Firebaseの初期化
    if "firebase_initialized" not in st.session_state:
        initialize_firebase()
        st.session_state["firebase_initialized"] = True

    # ログインセッション確認
    if "user" in st.session_state:
        st.sidebar.success(f"ログイン中: {st.session_state['user']['email']}")
        user_dashboard()
        return

    # タブで登録とログインを切り替える
    mode = st.radio("選択してください", ["ログイン", "新規登録"])

    if mode == "新規登録":
        st.subheader("新規登録")
        email = st.text_input("メールアドレス")
        password = st.text_input("パスワード", type="password")
        if st.button("登録"):
            user = register_user(email, password)
            if user:
                st.session_state["user"] = {"email": email, "uid": user.uid}
                st.session_state["rerun"] = not st.session_state.get("rerun", False)

    elif mode == "ログイン":
        st.subheader("ログイン")
        email = st.text_input("メールアドレス")
        password = st.text_input("パスワード", type="password")
        if st.button("ログイン"):
            success = login_user(email)
            if success:
                st.session_state["rerun"] = not st.session_state.get("rerun", False)

# アプリの起動
if __name__ == "__main__":
    # ローカル用に.envを読み込む（ローカル環境の場合のみ有効）
    if os.path.exists(".env"):
        load_dotenv()
    app()
