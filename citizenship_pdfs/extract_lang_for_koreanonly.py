import json
from pathlib import Path

INPUT_FILE = "multilang_2025_clean_v6.json"
OUTPUT_FILE = "ko_app.json"
TARGET_LANG = "ko"  # 한국어만 추출

def extract_lang(input_path: Path, output_path: Path, lang: str):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    extracted = []
    for item in data:
        base = {
            "id": item["id"],
            "question_en": item["question"],
            "answers_en": item.get("answers", []),
        }
        # 한국어 번역이 존재할 경우 추가
        if lang in item.get("translations", {}):
            tr = item["translations"][lang]
            base["question_ko"] = tr.get("question", "")
            base["answers_ko"] = tr.get("answers", [])
        else:
            base["question_ko"] = ""
            base["answers_ko"] = []

        extracted.append(base)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(extracted, f, ensure_ascii=False, indent=2)

    print(f"✅ Extracted {len(extracted)} Korean questions to {output_path}")

if __name__ == "__main__":
    extract_lang(Path(INPUT_FILE), Path(OUTPUT_FILE), TARGET_LANG)
