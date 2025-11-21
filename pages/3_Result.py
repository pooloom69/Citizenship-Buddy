import streamlit as st
from utils import session_manager

st.set_page_config(page_title="Result Summary", page_icon="📊")
session_manager.init_session()

st.header("Result Summary")

results = st.session_state.get("test_results", [])
if not results:
    st.warning("No test results found. Please take the test first.")
    st.stop()

# 점수 계산
correct_count = sum(1 for r in results if r["is_correct"])
total = len(results)
accuracy = round((correct_count / total) * 100, 1)

st.subheader(f"🏅 Your Score: {correct_count} / {total}  ({accuracy}%)")

# 오답 리스트 저장
wrong_questions = [r for r in results if not r["is_correct"]]
st.session_state["wrong_list"] = wrong_questions

# 결과 요약
with st.expander("📄 View Details"):
    for r in results:
        status = "✅" if r["is_correct"] else "❌"
        st.markdown(f"**{status} Question:** {r['question']}")
        st.markdown(f"**Your answer:** `{r['your_answer']}`")
        if not r["is_correct"]:
            st.markdown(f"**Correct answer:** {r['correct_answer']}")
        st.write("---")

# 🔁 오답만 다시 풀기
if wrong_questions:
    st.button("🔁 Retry Wrong Answers", on_click=lambda: st.switch_page("pages/4_Review.py"))
else:
    st.success("🎉 Perfect score! No wrong answers to review.")

st.page_link("app.py", label="🏠 Back to Home")
