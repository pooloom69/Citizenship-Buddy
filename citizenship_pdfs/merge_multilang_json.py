import json, re
from pathlib import Path

INPUT = "multilang_2025_clean_v4.json"
OUTPUT = "multilang_2025_clean_v6.json"

def clean_text(txt: str) -> str:
    """Remove footer junk, version markers, numbers, and stray whitespace."""
    if not isinstance(txt, str):
        return txt
    patterns = [
        r"128\s*Civics\s*Questions.*?(version\s*\d{4}|버전|\)|\])",
        r"市民権に関する128の質問.*?年版",
        r"128\s*(Вопросов|Питань).*?верс(ия|ія)",
        r"128\s*(preguntas|questions|問).*?(versión|版)",
        r"\b\d{1,3}\s*\)",  # dangling numbers like "30 )"
        r"\s*버전.*$",      # Korean footer
        r"B:\s*\d{3,4}s",   # "B: 1800s" etc
        r"(\s*14\s*)?시민권.*버전", 
        r"\s*\d+\s*128.*$", # "30 128 ..." etc
    ]
    for p in patterns:
        txt = re.sub(p, "", txt, flags=re.IGNORECASE)
    txt = re.sub(r"\s{2,}", " ", txt).strip()
    return txt

def fix_common_typos(lang_block: dict, qid: int):
    """Language-specific typo and swap corrections."""
    if not lang_block: 
        return

    # 🇷🇺 Russian fixes
    if "ru" in lang_block:
        lang_block["ru"]["answers"] = [
            a.replace("Генеральний", "Генеральный")
             .replace("сельського", "сельского")
             .replace("Агенства", "Агентства")
            for a in lang_block["ru"].get("answers", [])
        ]

    # 🇺🇦 Ukrainian fixes
    if "uk" in lang_block:
        q = lang_block["uk"]["question"]
        lang_block["uk"]["question"] = q.replace("від Британіїомий", "відомий багатьма речами")

    # 🇨🇳 Chinese 89–90 swap correction
    if qid == 89 and "zh" in lang_block:
        zh_q = lang_block["zh"]["question"]
        if "What territory" in zh_q or "美国" in zh_q and "1803" in zh_q:
            lang_block["zh"]["question"] = "亚历山大·汉密尔顿因许多事而闻名。请说出一件。"
            lang_block["zh"]["answers"] = [
                "第一任财政部长",
                "《联邦党人文集》的作者之一",
                "帮助建立美国第一银行",
                "乔治·华盛顿将军的副官",
                "大陆会议成员"
            ]
    if qid == 90 and "zh" in lang_block:
        zh_q = lang_block["zh"]["question"]
        if "Name one war" in zh_q or "战争" in zh_q and "1800" in zh_q:
            lang_block["zh"]["question"] = "美国在1803年从法国购买了哪一片领土？"
            lang_block["zh"]["answers"] = ["路易斯安那领地", "路易斯安那"]

    return lang_block

def normalize_answers(block):
    """Clean each text field in question and all translations."""
    block["question"] = clean_text(block["question"])
    block["answers"] = [clean_text(a) for a in block.get("answers", [])]
    for lang in block.get("translations", {}):
        t = block["translations"][lang]
        t["question"] = clean_text(t["question"])
        t["answers"] = [clean_text(a) for a in t.get("answers", [])]
    return block

def main():
    data = json.load(open(INPUT, "r", encoding="utf-8"))
    cleaned = []
    for q in data:
        qid = q["id"]
        # 1️⃣ Fix JD Vance for VP question
        if qid == 39:
            vp = "JD Vance"
            uniform = [f"The Vice President of the United States is {vp}."]
            q["answers"] = uniform
            for lang in q["translations"]:
                q["translations"][lang]["answers"] = uniform
        # 2️⃣ Fix language typos and swaps
        q["translations"] = fix_common_typos(q.get("translations", {}), qid)
        # 3️⃣ Clean all texts
        q = normalize_answers(q)
        cleaned.append(q)

    json.dump(cleaned, open(OUTPUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"✅ Cleaned JSON saved to {OUTPUT}")
    print(f"Total questions processed: {len(cleaned)}")

if __name__ == "__main__":
    main()



# 📘 진행 로그 / 작업 코멘트 (2025.11.09 기준)

# PDF 다국어 데이터 추출 완료

# 언어별 128-Civics-Questions-and-Answers-[언어].pdf에서 OCR + pdfplumber 혼합 방식으로 추출

# 한국어, 중국어, 일본어, 프랑스어, 스페인어, 러시아어, 우크라이나어, 베트남어, 폴란드어까지 확보

# 기본 병합 및 구조 정비

# 영어 원본(2025-Civics-Test-128-Questions-and-Answers.json)과 각 언어 매칭

# merge_multilang_json.py → merge_multilang_final_v3.py → multilang_2025_clean_v4/v5/v6 단계별 개선

# 자동 후처리(정제)

# 버전 꼬리표 / 페이지 넘버 제거

# “JD Vance” 부통령 자동 반영

# 중국어 89–90 swap 교정, 러시아어·우크라이나어 오타 수정

# 바닥글 및 128 Civics Questions… 같은 노이즈 제거

# 최종 결과물: multilang_2025_clean_v6.json

# 현재까지 한계점

# 일부 언어의 줄바꿈 및 문체 불균일(특히 중국어, 러시아어)

# 10% 정도의 의미 불일치 남아있음 (수동 검수 필요)

# 앱 1차 적용용 데이터로는 충분히 안정적