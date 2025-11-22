import streamlit as st
import base64
from openai import OpenAI

def get_client():
    # 여러 Key name을 대응 (Cloud 호환)
    for key in ["OPENAI_API_KEY", "openai_api_key", "OPENAI", "openai"]:
        if key in st.secrets:
            return OpenAI(api_key=st.secrets[key])
    raise ValueError("❗ OpenAI API Key not found in Streamlit secrets.")

# --------------------------------------------------------------
# 🎧 TEXT → SPEECH (모바일 완전 호환)
# --------------------------------------------------------------
def play_tts(text):
    client = get_client()

    # 1) TTS 생성
    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    )

    # 2) 바이트로 변환
    audio_bytes = response.read()

    # 3) base64로 인코딩
    audio_b64 = base64.b64encode(audio_bytes).decode()

    # 4) HTML audio 태그로 넣기 (모바일 100% 지원)
    st.markdown(
        f"""
        <audio controls>
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>
        """,
        unsafe_allow_html=True
    )

# --------------------------------------------------------------
# 🎤 RECORD + WHISPER STT
# --------------------------------------------------------------
def record_and_transcribe():
    client = get_client()

    audio = st.audio_input("🎤 Record your voice")
    if audio is None:
        return None

    with st.spinner("📥 Transcribing your recording..."):
        transcript = client.audio.transcriptions.create(
            model="whisper-1",    # ← 반드시 whisper-1!
            file=audio
        )
        text = transcript.text

    st.success("🎉 Transcription completed!")
    st.markdown(f"🗣️ You said: **{text}**")
    return text
