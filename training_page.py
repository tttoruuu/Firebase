from firebase import db
import streamlit as st

def switch_page(page_name):
    st.session_state["current_page"] = page_name

def training_page():
    uid = st.session_state["user"]["uid"]
    user_ref = db.collection("users").document(uid)
    user_data = user_ref.get().to_dict()
    
    with st.form(key="mbti_form"):
        availabletime = str(st.slider("今日使える時間(分)", 5,120,360))    
        submit_btn = st.form_submit_button(label="登録")

    if submit_btn:
        st.text(f"ようこそ！{user_data['name']}さん！") 
        st.text(f"{user_data['name']}さんのやりたいことを応援するね！")
        st.text("さっそく今日やることを決めよう")

        st.button("Done！", on_click=lambda: switch_page("成果"))