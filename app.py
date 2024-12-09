import streamlit as st
from firebase_admin import credentials, initialize_app, auth, firestore
import firebase_admin

# Firebaseの初期化
def initialize_firebase():
    if not firebase_admin._apps:  # Firebaseアプリが初期化されていない場合のみ実行
        # Streamlit SecretsからFirebaseサービスアカウントキーを取得
        firebase_secrets = dict(st.secrets["firebase"])  # dict型に変換
        cred = credentials.Certificate(firebase_secrets)
        initialize_app(cred)

    return firestore.client()

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

# ユーザー情報入力ページ
def user_dashboard():
    st.title("ユーザー情報を入力")
    uid = st.session_state["user"]["uid"]

    mbti = st.selectbox("あなたのMBTIを選択してください", ["ENFP", "INTJ", "INFJ", "ENTP", "その他"])
    habit_goal = st.text_input("習慣化したいことを入力してください")

    if st.button("保存"):
        save_user_data(uid, mbti, habit_goal)

# Streamlit UI
def app():
    st.title("Firebase Authentication Example")

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
            register_user(email, password)

    elif mode == "ログイン":
        st.subheader("ログイン")
        email = st.text_input("メールアドレス")
        password = st.text_input("パスワード", type="password")
        if st.button("ログイン"):
            if login_user(email):
                st.experimental_rerun()  # ページを再読み込みしてログイン状態を反映

# アプリの起動
if __name__ == "__main__":
    app()
