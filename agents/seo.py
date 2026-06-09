import anthropic
from typing import Any
from config import ANTHROPIC_API_KEY, MODEL_HAIKU
from utils.seo_parser import parse_seo
from utils.seo_title_checker import check_seo_title

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SEO_PROMPT = """
당신은 한국 블로그 SEO 분석가입니다.
초안을 분석해서 아래 JSON 형식으로만 출력하세요.
마크다운 코드블록(```) 없이 순수 JSON만 출력하세요.

{
  "title": "제목",
  "meta_description": "메타디스크립션",
  "tags": ["태그1", "태그2", "태그3", "태그4", "태그5"]
}

제목 규칙:
- 60자 이내, 검색 의도에 맞는 표현 사용
- 아래 스타일을 다양하게 섞을 것 (한 패턴 반복 금지):
  · 질문형: "왜 ~일까?", "~해도 되나?"
  · 경험형: "~했더니 생긴 일", "2시간 삽질기"
  · 직접형: "~ 완전 정복", "~ 제대로 하는 법"
  · 숫자형: "3가지 ~" (전체 제목 중 1/3 이하로 사용)

메타디스크립션 규칙:
- 핵심 키워드 자연스럽게 포함
- 독자가 얻을 수 있는 것을 명확히
- 150자 이내

태그 규칙:
- 실제 검색량 있는 롱테일 키워드 위주
- 너무 광범위한 태그(예: "IT", "컴퓨터") 지양
- 글 내용과 직접 관련된 구체적 키워드
"""

def run(state: dict[str, Any]) -> dict[str, Any]:
    draft = state["draft"]
    keywords = state.get("keywords", [""])
    main_keyword = keywords[0] if keywords else ""

    response = client.messages.create(
        model=MODEL_HAIKU,
        max_tokens=512,
        system=SEO_PROMPT,
        messages=[{"role": "user", "content": f"초안:\n{draft[:8000]}"}]
    )

    result = next(block.text for block in response.content if hasattr(block, "text"))
    parsed = parse_seo(result)
    title_check = check_seo_title(parsed.get("title", ""), main_keyword)

    return {
        **state,
        "seo": {"raw": result, "parsed": parsed, "title_check": title_check},
        "messages": [{"role": "seo", "content": result}]
    }
