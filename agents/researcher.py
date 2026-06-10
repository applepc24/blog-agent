import anthropic
import time
from typing import Any
from config import ANTHROPIC_API_KEY, MODEL_HAIKU
from utils.trend_analyzer import score_keywords

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

CORE_KEYWORD_PROMPT = """
블로그 주제를 보고 한국인이 실제로 검색하는 핵심 키워드 10개를 생성하세요.

규칙:
- 반드시 2~3단어 조합 (예: "야식 다이어트", "파이썬 독학", "저탄수 식단")
- 1단어짜리 광범위한 키워드 금지 (예: "다이어트", "파이썬")
- 문장형 절대 금지 (예: "야식 끊고 살 빠지는 시간" 이런 거 금지)
- 한 줄에 키워드 하나씩, 번호 없이 출력
"""

LONGTAIL_PROMPT = """
아래 핵심 키워드들을 바탕으로 '눕고싶은 취준생의 생존일지' 블로그에 맞는 롱테일 키워드를 만드세요.

블로그 타겟: 비전공자 취준생, 일반인
조건:
- 핵심 키워드 + 취준생/초보자/비전공자 관점 조합
- 경쟁이 낮을 것 같은 구체적인 표현
- 검색하는 사람의 의도가 명확한 키워드
- 한 줄에 하나씩, 번호 없이 출력
"""

RETRY_PROMPT = """
아래 주제를 비슷하지만 다른 각도로 표현한 핵심 키워드 10개를 생성하세요.
원래 주제와 유사하되, 더 구체적이거나 다른 표현을 사용하세요.

규칙:
- 반드시 2~3단어 조합
- 1단어짜리 광범위한 키워드 금지
- 문장형 절대 금지
- 한 줄에 키워드 하나씩, 번호 없이 출력
"""

def _generate_core_keywords(topic: str, prompt: str) -> list[str]:
    resp = client.messages.create(
        model=MODEL_HAIKU,
        max_tokens=512,
        system=prompt,
        messages=[{"role": "user", "content": f"주제: {topic}"}]
    )
    raw = next(block.text for block in resp.content if hasattr(block, "text"))
    return [line.strip() for line in raw.strip().splitlines() if line.strip()][:10]


def run(state: dict[str, Any]) -> dict[str, Any]:
    topic = state["topic"]
    t_start = time.time()
    input_tokens = 0
    output_tokens = 0

    # 1단계: 핵심 키워드 생성
    core_candidates = _generate_core_keywords(topic, CORE_KEYWORD_PROMPT)

    # 2단계: 트렌드 점수 확인
    scored = score_keywords(core_candidates)
    top_cores = [k for k in scored if k["score"] > 0][:5]

    low_traffic_warning = False

    # 3단계: 전부 0점이면 유사 키워드로 1회 재시도
    if not top_cores:
        retry_candidates = _generate_core_keywords(topic, RETRY_PROMPT)
        retry_scored = score_keywords(retry_candidates)
        top_cores = [k for k in retry_scored if k["score"] > 0][:5]

        if not top_cores:
            low_traffic_warning = True
            top_cores = retry_scored[:3]

    core_list = "\n".join(k["keyword"] for k in top_cores)

    # 4단계: 수요 있는 핵심 키워드 → 롱테일 변환
    resp2 = client.messages.create(
        model=MODEL_HAIKU,
        max_tokens=512,
        system=LONGTAIL_PROMPT,
        messages=[{"role": "user", "content": f"주제: {topic}\n핵심 키워드:\n{core_list}"}]
    )
    input_tokens += resp2.usage.input_tokens
    output_tokens += resp2.usage.output_tokens

    raw2 = next(block.text for block in resp2.content if hasattr(block, "text"))
    longtail_keywords = [line.strip() for line in raw2.strip().splitlines() if line.strip()][:3]

    pairs = list(zip(longtail_keywords, top_cores))
    summary = "\n".join(
        f"{i+1}. {kw} (핵심: {core['keyword']}, 네이버: {core['naver_score']}, 구글: {core['google_score']})"
        for i, (kw, core) in enumerate(pairs)
    )

    return {
        **state,
        "keywords": [summary],
        "low_traffic_warning": low_traffic_warning,
        "messages": [{"role": "researcher", "content": summary}],
        "agent_tokens": [{"agent": "researcher", "input_tokens": input_tokens,
                          "output_tokens": output_tokens, "duration_sec": round(time.time() - t_start, 2)}]
    }
