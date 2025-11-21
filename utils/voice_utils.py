import os
import tempfile
import streamlit as st
from openai import OpenAI
import base64

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------------------------------------------
# 🎙️ 녹음 및 Whisper 변환
# ---------------------------------------------------
def record_and_transcribe():
    """
    ✅ Streamlit 내장형 Recorder로 음성 녹음 → Whisper로 텍스트 변환
    """
    st.markdown("### 🎤 Record your answer below")
    st.caption("Click the button to start and stop recording.")

    # 🟢 streamlit 최신 버전의 내장 오디오 녹음기 (2025 기준)
    audio_bytes = st.audio_input("Record your voice")

    if audio_bytes is not None:
        # st.success("✅ Recording received. Transcribing...")

        # 임시 WAV 파일 생성
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes.getbuffer())
            tmp_path = tmp.name

        try:
            with open(tmp_path, "rb") as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f
                )
            text = transcript.text.strip()
            os.remove(tmp_path)
            st.session_state["user_answer"] = text
            st.success(f"🗣️ You said: **{text}**")
            return text
        except Exception as e:
            st.error(f"Whisper error: {e}")
            return ""

    return ""


# ---------------------------------------------------
# 🔊 TEXT TO SPEECH
# ---------------------------------------------------
def play_tts(text, voice="alloy"):
    """
    질문을 음성으로 재생 (OpenAI TTS 사용)
    """
    st.session_state.pop("tts_audio_path", None)
    try:
        st.info("🔊 Generating audio...")
        speech = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=text,
        )
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp.write(speech.read())
        tmp.close()
        st.session_state["tts_audio_path"] = tmp.name

        with open(tmp.name, "rb") as f:
            st.audio(f.read(), format="audio/mp3")
    except Exception as e:
        st.error(f"TTS Error: {e}")
