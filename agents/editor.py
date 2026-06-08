import anthropic
from config import ANTHROPIC_API_KEY, MODEL_OPUS
from db.jangdokdae import get_pending_ideas

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

EDITOR_SYSTEM_PROMPT = """
You are the Editor-in-Chief of '눕고싶은 취준생의 생존일지' blog.

## Identity
- Blog owner: Junseok (non-CS background, data engineer job seeker)
- Topics: Dev/Data (70%), Diet/Health (30%)
- Goal: Google AdSense monetization via SEO

## Your ONLY responsibilities
1. Talk with Junseok via Discord
2. Check idea storage (장독대) → propose topics
3. Delegate tasks to sub-agents (researcher, writer, SEO)
4. Review and approve final draft

## Routing rules
- 장독대 있음 → propose to Junseok first
- 장독대 없음 → ASK Junseok, never decide alone
- Draft ready → show Junseok, wait for approval

## What you must NOT do
- Never write blog posts yourself
- Never make topic decisions without Junseok's approval
- Never call sub-agents without Junseok's go-ahead

## Tone
- Korean, casual, friendly
- Short and clear responses only
"""


async def chat(user_message: str, conversation_history: list) -> str:
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    response = client.messages.create(
        model=MODEL_OPUS,
        max_tokens=1024,
        system=EDITOR_SYSTEM_PROMPT,
        messages=conversation_history
    )

    assistant_message = next(block.text for block in response.content if hasattr(block, "text"))
    conversation_history.append({
        "role": "assistant",
        "content": assistant_message
    })

    return assistant_message


async def suggest_topic() -> str:
    ideas = await get_pending_ideas()

    if ideas:
        idea_list = "\n".join([f"- #{i['id']} {i['content']}" for i in ideas])
        prompt = f"장독대에 이런 글감들이 있어요:\n{idea_list}\n\n어떤 걸 먼저 써볼까요? 준석에게 제안해주세요."
    else:
        prompt = "장독대가 비어있어요. 요즘 트렌드 기반으로 글 주제를 준석에게 물어봐주세요."

    response = client.messages.create(
        model=MODEL_OPUS,
        max_tokens=512,
        system=EDITOR_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    return next(block.text for block in response.content if hasattr(block, "text"))
