import streamlit as st
from utils.question_loader import load_questions
from utils.voice_utils import record_and_transcribe, play_tts
from utils.ai_evaluator import evaluate_answer
from utils import session_manager


# ----------------------------------------------------
# 질문 데이터 존재 확인
# ----------------------------------------------------
if "questions" not in st.session_state or not st.session_state["questions"]:
    st.error("⚠️ No questions loaded. Please return to Home.")
    st.page_link("app.py", label="🏠 Back to Home")
    st.stop()


# ----------------------------------------------------
# 초기 세션 상태 설정
# ----------------------------------------------------
if "q_index" not in st.session_state:
    st.session_state.q_index = 0

if "user_answer" not in st.session_state:
    st.session_state.user_answer = ""

if "evaluated" not in st.session_state:
    st.session_state.evaluated = False

if "show_result" not in st.session_state:
    st.session_state.show_result = False


# ----------------------------------------------------
# 문제 로드 (모두 ko_app.json 기반)
# ----------------------------------------------------
questions = st.session_state["questions"]
q = questions[st.session_state.q_index]

st.markdown(f"### ❓ Question {st.session_state.q_index + 1}")
st.markdown(q["question_en"])

if st.session_state.get("lang") == "한국어 번역 보기":
    st.markdown(f"**🇰🇷 {q['question_ko']}**")


# ----------------------------------------------------
# 🔊 Listen
# ----------------------------------------------------
if st.button("🔊 Listen"):
    play_tts(q["question_en"])


# ----------------------------------------------------
# 🎤 Record Answer
# ----------------------------------------------------
user_input = record_and_transcribe()


# ----------------------------------------------------
# 🧠 정답 판정 (정답 텍스트는 안 보여줌)
# ----------------------------------------------------
if user_input and user_input.strip():
    st.session_state.user_answer = user_input.strip()
    st.session_state.evaluated = True

if st.session_state.evaluated and st.session_state.user_answer:
    result = evaluate_answer(q["answers_en"], st.session_state.user_answer)

    st.session_state["is_correct"] = result["is_correct"]
    st.session_state["ai_feedback"] = result["feedback"]

    if result["is_correct"]:
        st.success("🟢 Correct!")
    else:
        st.error("🔴 Incorrect!")
        session_manager.save_wrong(q, st.session_state.user_answer)


# ----------------------------------------------------
# 📘 정답 보기 (토글 버튼)
# ----------------------------------------------------
if st.button("Show/Hide Answer"):
    st.session_state.show_result = not st.session_state.show_result


# ----------------------------------------------------
# 📘 정답/한국어 해설 — 버튼 누를 시에만 표시 (Compact)
# ----------------------------------------------------
if st.session_state.show_result:

    # 영어 정답 카드
    st.markdown("""
    <div style="
        padding:10px 14px;
        background-color:#EEF3FF;
        border-radius:8px;
        border:1px solid #d0d7e2;
        margin-top:10px;
    ">
        <h5 style="margin:0; font-size:17px;">📘 Correct Answer(s)</h5>
    </div>
    """, unsafe_allow_html=True)

    for ans in q.get("answers_en", []):
        st.markdown(f"<div style='padding-left:8px; font-size:16px;'>• {ans}</div>", 
                    unsafe_allow_html=True)

    # 한국어 정답 카드
    if st.session_state.get("lang") == "한국어 번역 보기":

        st.markdown("""
        <div style="
            padding:10px 14px;
            background-color:#FFF5E5;
            border-radius:8px;
            border:1px solid #e6d8c7;
            margin-top:12px;
        ">
            <h5 style="margin:0; font-size:17px;">🇰🇷 한국어 번역된 정답</h5>
        </div>
        """, unsafe_allow_html=True)

        for ans in q.get("answers_ko", []):
            st.markdown(f"<div style='padding-left:8px; font-size:16px;'>• {ans}</div>", 
                        unsafe_allow_html=True)

# ----------------------------------------------------
# Navigation — centered [ ⬅ ] [ ➡ ]
# ----------------------------------------------------
st.write("---")
nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])

with nav_col1:
    prev_btn = st.button("⬅", key="prev_btn", use_container_width=True)

with nav_col3:
    next_btn = st.button("➡", key="next_btn", use_container_width=True)

# ----------------------------------------------------
# 이동 처리 + 상태 초기화
# ----------------------------------------------------
if prev_btn or next_btn:

    # 정답 관련 상태 초기화
    st.session_state.user_answer = ""
    st.session_state.evaluated = False
    st.session_state.show_result = False

    if next_btn:
        st.session_state.q_index = (st.session_state.q_index + 1) % len(questions)
    elif prev_btn:
        st.session_state.q_index = max(0, st.session_state.q_index - 1)

    st.rerun()


# ----------------------------------------------------
# Back to Home
# ----------------------------------------------------
st.write("---")
st.page_link("app.py", label="🏠 Back to Home")
st.caption("Developed by Sola | AI Citizenship Coach MVP v0.1")