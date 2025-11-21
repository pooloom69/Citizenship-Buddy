# 📄 extract_lang_qa.py
import pdfplumber
import json
import re
from pathlib import Path

def extract_lang_qa(pdf_path: str, lang_code: str):
    """언어별 PDF에서 질문·답을 추출하여 {lang}.json 저장"""
    pdf_path = Path(pdf_path)
    output_path = pdf_path.with_suffix(".json")

    data = []
    q_pattern = re.compile(r"^\s*\d{1,3}\.")  # "1." "25." 같은 번호 패턴
    current_q = None

    print(f"📘 Extracting {lang_code.upper()} from {pdf_path.name}")

    with pdfplumber.open(pdf_path) as pdf:
        lines = []
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines += [l.strip() for l in text.split("\n") if l.strip()]

    for line in lines:
        if q_pattern.match(line):
            # 새로운 질문 시작
            if current_q:
                data.append(current_q)
            qnum = int(line.split(".")[0])
            qtext = line[line.find(".") + 1:].strip()
            current_q = {"id": qnum, "question": qtext, "answers": []}
        elif line.startswith("●") or line.startswith("-") or line.startswith("•"):
            if current_q:
                ans = re.sub(r"^[●•\-]+\s*", "", line).strip()
                current_q["answers"].append(ans)
        else:
            # 답이 여러 줄인 경우 이어 붙이기
            if current_q and current_q["answers"]:
                current_q["answers"][-1] += " " + line.strip()

    if current_q:
        data.append(current_q)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {output_path.name} ({len(data)} questions)")
    return data

if __name__ == "__main__":
    extract_lang_qa("2025-Civics-Test-128-Questions-and-Answers.pdf", "en")


# if __name__ == "__main__":
#     files = [
#         ("128-Civics-Questions-and-Answers-Japanese.pdf", "ja"),
#         ("128-Civics-Questions-and-Answers-French.pdf", "fr"),
#         ("128-Civics-Questions-and-Answers-Spanish.pdf", "es"),
#         ("128-Civics-Questions-and-Answers-Russian.pdf", "ru"),
#         ("128-Civics-Questions-and-Answers-Ukrainian.pdf", "uk"),
#         ("128-Civics-Questions-and-Answers-Vietnamese.pdf", "vi"),
#     ]

#     for pdf_file, code in files:
#         extract_lang_qa(pdf_file, code)
