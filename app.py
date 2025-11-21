import streamlit as st
from utils import session_manager
from dotenv import load_dotenv
load_dotenv()

from utils.question_loader import load_questions

# ----------------------------------------------------
# Session state initialization
# ----------------------------------------------------
if "q_index" not in st.session_state:
    st.session_state.q_index = 0

# 앱 시작 시 자동으로 2025(한국어 버전 포함) 로드
if "questions" not in st.session_state:
    st.session_state.questions = load_questions()



st.set_page_config(page_title="AI Citizenship Coach", page_icon="🇺🇸", layout="centered")

session_manager.init_session()

st.title("🇺🇸 AI Citizenship Coach")
st.markdown("### Practice for your U.S. citizenship test with AI voice and feedback.")

# 선택 항목
st.subheader("Choose Test Version")
version = st.radio("Select the question set:", [ "2025"], horizontal=True) # delete 2008 for now
st.session_state["version"] = version

st.subheader("Language")
lang = st.radio("Select language:", ["English", "한국어 번역 보기"], horizontal=True)
st.session_state["lang"] = lang

st.write("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("▶ Start Practice"):
        st.switch_page("pages/1_Practice.py")

with col2:
    if st.button("🧩 Take a Test"):
        st.switch_page("pages/2_Test.py")

st.write("---")
st.caption("Developed by Sola | AI Citizenship Coach MVP v0.1")
