import json
import re
import pdfplumber
from pathlib import Path

# === 기본 설정 ===
BASE_DIR = Path(__file__).resolve().parent
PDF_DIR = BASE_DIR
OUTPUT_JSON = BASE_DIR / "questions_2025_multilang_v2.json"

BASE_PDF = "2025-Civics-Test-128-Questions-and-Answers.pdf"

# === 언어 파일 매핑 (깨짐 언어 제외) ===
LANG_FILES = {
    "zh": "128-Civics-Questions-and-Answers-Chinese.pdf",
    "fr": "128-Civics-Questions-and-Answers-French.pdf",
    "de": "128-Civics-Questions-and-Answers-German.pdf",
    "ht": "128-Civics-Questions-and-Answers-HaitianCreole.pdf",
    "ja": "128-Civics-Questions-and-Answers-Japanese.pdf",
    "ko": "128-Civics-Questions-and-Answers-Korean.pdf",
    "pl": "128-Civics-Questions-and-Answers-Polish.pdf",
    "ru": "128-Civics-Questions-and-Answers-Russian.pdf",
    "es": "128-Civics-Questions-and-Answers-Spanish.pdf",
    "sw": "128-Civics-Questions-and-Answers-Swahili.pdf",
    "tl": "128-Civics-Questions-and-Answers-Tagalog.pdf",
    "uk": "128-Civics-Questions-and-Answers-Ukrainian.pdf",
    "vi": "128-Civics-Questions-and-Answers-Vietnamese.pdf",
}
SKIP_LANGS = {"ar", "hi", "ne"}  # 깨짐 언어 스킵

# === 공통 함수 ===
def extract_text_from_pdf(pdf_path):
    text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            raw = page.extract_text()
            if raw:
                text.append(raw)
    return "\n".join(text)

def parse_base_questions(raw_text):
    """영문 기준 문항 파싱"""
    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
    qas, current_q, current_a = [], None, []
    for line in lines:
        if re.match(r"^\d+\.", line):
            if current_q:
                qas.append({"question": current_q, "answers": current_a})
            current_q = line.split(".", 1)[1].strip()
            current_a = []
        elif line.startswith(("●", "-", "•")):
            current_a.append(line.lstrip("●-• ").strip())
    if current_q:
        qas.append({"question": current_q, "answers": current_a})
    return qas

def parse_multilang_questions(raw_text):
    """
    다국어 PDF용 파서
    영어와 현지어가 섞여 있을 경우 한 쌍으로 묶음
    """
    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
    pattern_q = re.compile(r"^\d+\.")
    qas, current_q, current_a, current_trans_q, current_trans_a = [], None, [], None, []
    i = 0
    while i < len(lines):
        line = lines[i]

        # 영어 질문 감지
        if pattern_q.match(line):
            if current_q:
                qas.append({
                    "question": current_q,
                    "answers": current_a,
                    "translated_question": current_trans_q,
                    "translated_answers": current_trans_a
                })
            current_q = line.split(".", 1)[1].strip()
            current_a, current_trans_q, current_trans_a = [], None, []

            # 영어 답변 수집
            j = i + 1
            while j < len(lines) and (lines[j].startswith(("●", "-", "•"))):
                current_a.append(lines[j].lstrip("●-• ").strip())
                j += 1
            # 비ASCII 라인 = 번역 질문
            if j < len(lines) and not re.match(r"^[ -~]+$", lines[j]):
                current_trans_q = lines[j].strip()
                j += 1
                # 번역 답변
                while j < len(lines) and (lines[j].startswith(("●", "-", "•"))):
                    current_trans_a.append(lines[j].lstrip("●-• ").strip())
                    j += 1
            i = j
        else:
            i += 1

    if current_q:
        qas.append({
            "question": current_q,
            "answers": current_a,
            "translated_question": current_trans_q,
            "translated_answers": current_trans_a
        })
    return qas


def main():
    print("📘 Extracting English base questions...")
    base_text = extract_text_from_pdf(PDF_DIR / BASE_PDF)
    base_data = parse_base_questions(base_text)

    # 기본 구조화
    for i, q in enumerate(base_data, 1):
        q["id"] = i
        q["year"] = 2025
        q["translations"] = {}

    # 다국어 매칭
    for lang, fname in LANG_FILES.items():
        pdf_path = PDF_DIR / fname
        if not pdf_path.exists():
            print(f"⚠️ Missing file: {fname}")
            continue
        print(f"🌍 Processing {lang}...")

        raw_text = extract_text_from_pdf(pdf_path)
        qa_list = parse_multilang_questions(raw_text)

        for i, qa in enumerate(qa_list[: len(base_data)]):
            if qa["translated_question"]:
                base_data[i]["translations"][lang] = {
                    "question": qa["translated_question"],
                    "answers": qa["translated_answers"],
                }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(base_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
