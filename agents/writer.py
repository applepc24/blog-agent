import anthropic
import time
from typing import Any
from config import ANTHROPIC_API_KEY, MODEL_SONNET

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

WRITER_PROMPT = """
당신은 '눕고싶은 취준생의 생존일지' 블로그의 전담 라이터입니다.
블로그 주인 준석은 비전공자 데이터 엔지니어 취준생으로, 개발/데이터 공부와 건강 관리를 병행하고 있습니다.

## 글쓰기 스타일

**말투**
- "~해요", "~했어요", "~더라고요" 체 사용
- "솔직히", "근데", "그래서" 같은 자연스러운 연결어 활용
- ㅋㅋ, ㅠㅠ 같은 자모체 사용 금지

**구조**
- 도입부: 독자가 공감할 수 있는 구체적인 상황/장면으로 시작
- 핵심 먼저: 결론부터 말하고 설명이 따라오는 방식
- 문단: 3~5줄로 짧게 끊어쓰기
- 각 섹션 끝에 한 줄 정리
- h2 소제목으로 명확하게 구분

**톤**
- 솔직한 실패담과 경험 포함 ("처음엔 저도 몰랐어요", "근데 해보니 ~더라고요")
- 전문 용어는 비전공자도 이해하게 쉽게 풀어서 설명
- 독자에게 말 거는 느낌 ("여러분도 이런 경험 있으시죠?")

## 조건
- 1500자 이상
- h1/h2 마크다운 구조 사용
- 검색 의도에 정확히 답하는 글
- 준석의 경험/참고 내용이 제공되면 반드시 글에 자연스럽게 녹여낼 것
"""

def revise(draft: str, feedback: str, topic: str) -> dict[str, Any]:
    t_start = time.time()
    prompt = f"""다음은 '{topic}' 주제의 블로그 초안이에요.

아래 수정 요청을 **반드시 모두** 반영해서 전체 초안을 다시 작성해주세요.
수정 요청에 해당하는 부분은 확실하게 바꿔주세요. 애매하게 조금만 바꾸면 안 돼요.

=== 수정 요청 ===
{feedback}

=== 현재 초안 ===
{draft}

위 수정 요청을 전부 반영한 완성된 초안 전체를 출력해주세요."""

    response = client.messages.create(
        model=MODEL_SONNET,
        max_tokens=8192,
        system=WRITER_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    result = next(block.text for block in response.content if hasattr(block, "text"))

    return {
        "draft": result,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "duration_sec": round(time.time() - t_start, 2)
    }


def run(state: dict[str, Any]) -> dict[str, Any]:
    topic = state["topic"]
    keywords = state["keywords"]
    raw_material = state.get("raw_material", "")
    t_start = time.time()

    raw_section = f"\n\n준석의 경험/참고 내용:\n{raw_material}" if raw_material else ""
    prompt = f"주제: {topic}\n키워드 리서치 결과:\n{keywords[0]}{raw_section}\n\n위 내용을 바탕으로 블로그 초안을 작성해주세요."

    response = client.messages.create(
        model=MODEL_SONNET,
        max_tokens=8192,
        system=WRITER_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    result = next(block.text for block in response.content if hasattr(block, "text"))

    return {
        **state,
        "draft": result,
        "messages": [{"role": "writer", "content": "초안 작성 완료"}],
        "agent_tokens": [{"agent": "writer", "input_tokens": response.usage.input_tokens,
                          "output_tokens": response.usage.output_tokens, "duration_sec": round(time.time() - t_start, 2)}]
    }
