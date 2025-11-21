import streamlit as st
from utils import ai_evaluator, voice_utils

st.set_page_config(page_title="Review Wrong Answers", page_icon="🗂️")
st.header("🗂️ Review Wrong Answers")

# 🔹 Load wrong answer list
wrongs = st.session_state.get("wrong_list", [])
if not wrongs:
    st.info("No wrong answers recorded. ✅")
    st.page_link("app.py", label="🏠 Back to Home")
    st.stop()

# 🔹 Initialize review index
if "review_index" not in st.session_state:
    st.session_state["review_index"] = 0

idx = st.session_state["review_index"]
q = wrongs[idx]

# ------------------------------------------------------
# ❌ Show Question (English)
# ------------------------------------------------------
question_text = q.get("question_en") or q.get("question") or "No question text found"
st.subheader(f"❌ {question_text}")

# ------------------------------------------------------
# 📘 Correct Answers (English)
# ------------------------------------------------------
correct_answers = q.get("answers_en", [])

st.caption("Correct Answer(s):")
for ans in correct_answers:
    st.markdown(f"- **{ans}**")

# ------------------------------------------------------
# 🔊 Listen to the question
# ------------------------------------------------------
if st.button("🔊 Listen to Question"):
    voice_utils.play_tts(question_text)

# ------------------------------------------------------
# 🎤 Try Again (Record Answer)
# ------------------------------------------------------
user_input = voice_utils.record_and_transcribe()

if user_input:
    result = ai_evaluator.evaluate_answer(correct_answers, user_input)
    st.markdown(result["feedback"])

# ------------------------------------------------------
# ⏮ Back / ➡ Next Navigation
# ------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    if st.button("⏮ Back", disabled=(idx == 0)):
        st.session_state["review_index"] = max(0, idx - 1)
        st.rerun()

with col2:
    if st.button("➡ Next"):
        if idx + 1 < len(wrongs):
            st.session_state["review_index"] = idx + 1
            st.rerun()
        else:
            st.success("🎉 Review completed!")
            st.page_link("app.py", label="🏠 Back to Home")

# ------------------------------------------------------
# Footer
# ------------------------------------------------------
st.caption(f"Question {idx + 1} of {len(wrongs)}")
