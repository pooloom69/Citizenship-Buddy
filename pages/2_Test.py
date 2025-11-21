import random
import streamlit as st
from utils import question_loader, ai_evaluator, session_manager, voice_utils

st.set_page_config(page_title="Test Mode", page_icon="🧠")
session_manager.init_session()
st.header("Citizenship Test Simulation")

# -------------------------------------------------------
# 🔹 Load unified bilingual questions (ko_app.json)
# -------------------------------------------------------
questions = question_loader.load_questions()   # version 제거됨


# -------------------------------------------------------
# 🔹 Initialize Test Session
# -------------------------------------------------------
def start_new_test():
    st.session_state["test_questions"] = random.sample(questions, 12)
    st.session_state["test_index"] = 0
    st.session_state["test_results"] = []
    st.session_state.pop("user_answer", None)
    st.rerun()


# 첫 실행 시 초기화
if "test_questions" not in st.session_state:
    start_new_test()


# -------------------------------------------------------
# 🔹 Current Question
# -------------------------------------------------------
q_index = st.session_state["test_index"]
q = st.session_state["test_questions"][q_index]

# 언어 설정 (Practice와 동일)
lang = st.session_state.get("lang", "English")

st.subheader(f"Q{q_index + 1}. {q['question_en']}")

if lang == "한국어 번역 보기":
    st.markdown(f"**🇰🇷 {q['question_ko']}**")


# -------------------------------------------------------
# 🔊 Listen Button
# -------------------------------------------------------
if st.button("🔊 Listen to Question"):
    voice_utils.play_tts(q["question_en"])


# -------------------------------------------------------
# 🎙️ Record & Transcribe
# -------------------------------------------------------
user_input = voice_utils.record_and_transcribe()

if user_input:
    st.session_state["user_answer"] = user_input
    # st.success(f"🗣️ Your answer: {user_input}")


# -------------------------------------------------------
# 🧠 Answer Evaluation
# -------------------------------------------------------
if st.session_state.get("user_answer"):

    correct_answers = q.get("answers_en", [])   # ko_app.json 기준

    result = ai_evaluator.evaluate_answer(
        correct_answers,
        st.session_state["user_answer"]
    )

    # 저장된 결과가 부족하면 append, 아니면 수정
    if q_index >= len(st.session_state["test_results"]):
        st.session_state["test_results"].append({
            "question": q["question_en"],
            "your_answer": st.session_state["user_answer"],
            "correct_answer": ", ".join(correct_answers),
            "is_correct": result["is_correct"]
        })
    else:
        st.session_state["test_results"][q_index]["your_answer"] = st.session_state["user_answer"]
        st.session_state["test_results"][q_index]["is_correct"] = result["is_correct"]


# -------------------------------------------------------
# ⏮️ Back / ➡️ Next / 🔁 Retry Buttons
# -------------------------------------------------------
col1, col2, col3 = st.columns(3)

# ⏮️ Back
with col1:
    if st.button("⏮️ Back", disabled=(q_index == 0)):
        st.session_state["test_index"] -= 1
        st.session_state.pop("user_answer", None)
        st.rerun()

# ➡️ Next
with col2:
    if st.button("➡️ Next"):
        if q_index + 1 < len(st.session_state["test_questions"]):
            st.session_state["test_index"] += 1
            st.session_state.pop("user_answer", None)
            st.rerun()
        else:
            st.success("🎉 Test completed!")
            st.switch_page("pages/3_Result.py")

# 🔁 Retry Test
with col3:
    if st.button("🔁 Retry Test"):
        start_new_test()


# -------------------------------------------------------
# 📊 Progress bar
# -------------------------------------------------------
st.write("---")
st.progress((q_index + 1) / len(st.session_state["test_questions"]))
st.caption(f"Question {q_index + 1} of 12")

st.page_link("app.py", label="🏠 Back to Home")
