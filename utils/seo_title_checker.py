import re

def check_seo_title(title: str, main_keyword: str = "") -> dict:
    warnings = []
    score = 100

    if len(title) > 60:
        warnings.append("제목이 너무 김 (60자 이내 권장)")
        score -= 15
    elif len(title) < 15:
        warnings.append("제목이 너무 짧음 (15자 이상 권장)")
        score -= 10

    if main_keyword and main_keyword not in title:
        warnings.append(f"핵심 키워드 '{main_keyword}' 누락")
        score -= 20

    if re.search(r'!{2,}|[▲▼★☆]{2,}|#{2,}', title):
        warnings.append("과한 기호 사용")
        score -= 10

    words = re.findall(r'\w+', title)
    if len(words) != len(set(w.lower() for w in words)):
        warnings.append("단어 반복 가능성")
        score -= 10

    return {
        "score": max(score, 0),
        "warnings": warnings
    }
