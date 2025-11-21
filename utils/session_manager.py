import streamlit as st

def init_session():
    defaults = {
        "version": "2008",
        "lang": "English",
        "wrong_list": []
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def save_wrong(q, user_answer):
    st.session_state["wrong_list"].append({
        "question": q.get("question", ""),
        "answers": q.get("answers", []),
        "user_answer": user_answer
    })