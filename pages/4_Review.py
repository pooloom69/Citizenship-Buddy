import streamlit as st
from utils import ai_evaluator, voice_utils

st.set_page_config(page_title="Review Wrong Answers", page_icon="🗂️")
st.header("🗂️ Review Wrong Answers")

# 저장된 오답 리스트
wrongs = st.session_state.get("wrong_list", [])
if not wrongs:
    st.info("No wrong answers recorded. ✅")
    st.page_link("app.py", label="🏠 Back to Home")
    st.stop()

# 현재 리뷰 인덱스
if "review_index" not in st.session_state:
    st.session_state["review_index"] = 0

idx = st.session_state["review_index"]
q = wrongs[idx]

# ------------------------------------------------------
# 질문 출력 (영어 기준)
# ------------------------------------------------------
st.subheader(f"❌ {q['question']}")

# 정답을 다시 리스트로 분리
correct_answers = [ans.strip() for ans in q["correct_answer"].split(",")]

st.caption("Correct answer(s):")
for ans in correct_answers:
    st.markdown(f"- **{ans}**")


# ------------------------------------------------------
# 🔊 Listen
# ------------------------------------------------------
if st.button("🔊 Listen to Question"):
    voice_utils.play_tts(q["question"])


# ------------------------------------------------------
# 🎙️ 사용자 다시 답변
# ------------------------------------------------------
user_input = voice_utils.record_and_transcribe()

if user_input:
    result = ai_evaluator.evaluate_answer(correct_answers, user_input)
    st.markdown(result["feedback"])


# ------------------------------------------------------
# ⏮ Back / ➡ Next navigation
# ------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    if st.button("⏮ Back", disabled=(idx == 0)):
        st.session_state["review_index"] -= 1
        st.rerun()

with col2:
    if st.button("➡ Next"):
        if idx + 1 < len(wrongs):
            st.session_state["review_index"] += 1
            st.rerun()
        else:
            st.success("🎉 Review completed!")
            st.page_link("app.py", label="🏠 Back to Home")


st.caption(f"Question {idx + 1} of {len(wrongs)}")
