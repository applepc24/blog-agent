import asyncio
import discord
from discord.ext import commands
from config import DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID
from db.jangdokdae import init_db, add_idea, get_pending_ideas
from db.analytics import init_analytics_db, start_run, finish_run, log_post, log_agent, get_summary, get_run_list, get_run_detail, calc_cost
from agents.editor import chat
from graph.workflow import app as workflow_app
from wordpress import upload_post, update_post, delete_post
from utils.seo_parser import parse_seo

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
conversation_history: list[dict] = []

@bot.event
async def on_ready():
    await init_db()
    await init_analytics_db()
    print(f"봇 온라인: {bot.user}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.channel.id != DISCORD_CHANNEL_ID:
        return

    if message.content.startswith("!편집장"):
        user_input = message.content[5:].strip()
        reply = await chat(user_input, conversation_history)
        await message.channel.send(reply)
        return

    await bot.process_commands(message)


@bot.command(name="글감")
async def save_idea(ctx, *, content: str):
    idea_id = await add_idea(content)
    await ctx.send(f"장독대에 저장했어요! (#{idea_id})\n>{content}")


@bot.command(name="장독대")
async def show_ideas(ctx):
    ideas = await get_pending_ideas()
    if not ideas:
        await ctx.send("장독대가 비어있어요!")
        return
    msg = "**장독대 글감 목록**\n"
    for idea in ideas:
        msg += f"- #{idea['id']} {idea['content']} ({idea['created_at'][:10]})\n"
    await ctx.send(msg)


@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("pong!")


@bot.command(name="도움말")
async def help_command(ctx):
    msg = """**📋 명령어 목록**
`!편집장 말` → 편집장(Opus)과 대화
`!글쓰기 주제` → 주제로 블로그 글 자동 작성
`!글감 내용` → 장독대에 글감 저장
`!장독대` → 글감 목록 조회
`!통계` → 누적 통계 요약
`!통계 목록` → 글별 실행 목록
`!통계 <번호>` → 특정 실행 상세 (예: !통계 3)
`!ping` → 봇 상태 확인
`!도움말` → 명령어 목록"""
    await ctx.send(msg)

@bot.command(name="글쓰기")
async def write_post(ctx, *, topic: str = ""):
    if not topic:
        ideas = await get_pending_ideas()
        if not ideas:
            await ctx.send("장독대가 비어있어요. 주제를 직접 입력해줘요.\n예: `!글쓰기 파이썬 비동기 처리`")
            return
        msg = "**장독대 글감 목록**\n"
        for i, idea in enumerate(ideas, 1):
            msg += f"`{i}` {idea['content']} (#{idea['id']})\n"
        msg += "\n번호 입력하면 그 글감으로 쓸게요. (취소: `취소`)"
        await ctx.send(msg)

        def msg_check_pick(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            pick = await bot.wait_for("message", timeout=60.0, check=msg_check_pick)
        except asyncio.TimeoutError:
            await ctx.send("60초 초과로 취소됐어요.")
            return

        if pick.content.strip() == "취소":
            await ctx.send("취소했어요!")
            return

        if not pick.content.strip().isdigit() or not (1 <= int(pick.content.strip()) <= len(ideas)):
            await ctx.send("올바른 번호가 아니에요. 취소할게요.")
            return

        selected = ideas[int(pick.content.strip()) - 1]
        topic = selected["content"]
        await ctx.send(f"📝 **'{topic}'** 글감으로 시작할게요!")

    await ctx.send(f"경험이나 참고할 내용 있으면 보내줘요. (없으면 `없음`)")

    def msg_check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", timeout=300.0, check=msg_check)
        raw_material = "" if msg.content.strip() == "없음" else msg.content.strip()
    except asyncio.TimeoutError:
        await ctx.send("5분 초과로 취소됐어요.")
        return

    await ctx.send("✍️ 키워드 리서치 중...")

    run_id = await start_run(topic)
    initial_state = {
        "topic": topic,
        "raw_material": raw_material,
        "keywords": [],
        "draft": "",
        "seo": {},
        "messages": [],
        "next": "",
        "low_traffic_warning": False,
        "agent_tokens": []
    }

    from agents import researcher as researcher_agent
    research_result = await asyncio.to_thread(researcher_agent.run, initial_state)

    if research_result.get("low_traffic_warning"):
        warn_msg = await ctx.send(
            f"이 주제는 검색량이 거의 없어요.\n"
            f"키워드: {research_result['keywords'][0][:200]}\n\n"
            f"그래도 진행할까요?"
        )
        await warn_msg.add_reaction("✅")
        await warn_msg.add_reaction("❌")

        def warn_check(reaction, user):
            return (
                user == ctx.author
                and str(reaction.emoji) in ["✅", "❌"]
                and reaction.message.id == warn_msg.id
            )
        try:
            reaction, _ = await bot.wait_for("reaction_add", timeout=60.0, check=warn_check)
        except asyncio.TimeoutError:
            await finish_run(run_id, "cancelled")
            await ctx.send("60초 초과로 취소됐어요.")
            return

        if str(reaction.emoji) == "❌":
            await finish_run(run_id, "cancelled")
            await ctx.send("취소했어요. 다른 주제로 다시 시도해보세요.")
            return

    await ctx.send("글 작성 시작할게요! 1~2분 걸려요...")
    try:
        result = await asyncio.to_thread(workflow_app.invoke, research_result)
    except Exception as e:
        await finish_run(run_id, "fail")
        await ctx.send(f"글 작성 실패: {e}")
        return

    seo = parse_seo(result["seo"].get("raw", ""))

    await ctx.send(f"**🔍 황금 키워드**\n{result['keywords'][0]}")
    await ctx.send(
        f"**📊 SEO 결과**\n"
        f"제목: {seo.get('title', '(없음)')}\n"
        f"메타: {seo.get('meta_description', '(없음)')}\n"
        f"태그: {', '.join(seo.get('tags', []))}"
    )

    from agents import writer as writer_agent
    current_draft = result["draft"]
    current_title = seo.get("title") or topic
    current_tags = seo.get("tags", [])
    focus_keyword = result["keywords"][0] if result["keywords"] else ""

    # 초안을 WP draft로 먼저 업로드
    await ctx.send("📄 WordPress draft로 저장 중...")
    try:
        post = await asyncio.to_thread(
            upload_post,
            current_title,
            current_draft,
            current_tags,
            "draft",
            focus_keyword
        )
    except Exception as e:
        await finish_run(run_id, "fail")
        await ctx.send(f"업로드 실패: {e}")
        return

    post_id = post.get("id")
    admin_link = f"https://comeandlook.site/wp-admin/post.php?post={post_id}&action=edit"

    while True:
        confirm_msg = await ctx.send(
            f"**초안이 draft로 저장됐어요.**\n"
            f"👉 {admin_link}\n\n"
            f"전체 글 읽어보고 결정해주세요. (30분 대기)\n"
            f"✅ 발행  ✏️ 수정  ❌ 삭제"
        )
        await confirm_msg.add_reaction("✅")
        await confirm_msg.add_reaction("✏️")
        await confirm_msg.add_reaction("❌")

        def check(reaction, user, _msg=confirm_msg):
            return (
                user == ctx.author
                and str(reaction.emoji) in ["✅", "✏️", "❌"]
                and reaction.message.id == _msg.id
            )

        try:
            reaction, _ = await bot.wait_for("reaction_add", timeout=1800.0, check=check)
        except asyncio.TimeoutError:
            await finish_run(run_id, "cancelled")
            await ctx.send(f"30분 초과로 취소됐어요. draft는 WP에 남아있어요.\n{admin_link}")
            return

        emoji = str(reaction.emoji)

        if emoji == "❌":
            try:
                await asyncio.to_thread(delete_post, post_id)
            except Exception:
                pass
            await finish_run(run_id, "cancelled")
            await ctx.send("draft 삭제했어요!")
            return

        elif emoji == "✏️":
            await ctx.send("어떤 부분 수정할까요? (예: 결론 더 따뜻하게, 도입부 짧게)")

            def feedback_check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                feedback_msg = await bot.wait_for("message", timeout=300.0, check=feedback_check)
            except asyncio.TimeoutError:
                await ctx.send("5분 초과로 취소됐어요.")
                return

            await ctx.send("✍️ 수정 중... 30초~1분 걸려요.")
            try:
                revise_result = await asyncio.to_thread(
                    writer_agent.revise,
                    current_draft,
                    feedback_msg.content,
                    topic
                )
            except Exception as e:
                await ctx.send(f"수정 실패: {e}\n다시 시도해볼까요?")
                continue

            current_draft = revise_result["draft"]
            result["agent_tokens"].append({
                "agent": "writer_revise",
                "input_tokens": revise_result["input_tokens"],
                "output_tokens": revise_result["output_tokens"],
                "duration_sec": revise_result["duration_sec"]
            })

            # WP draft 내용 업데이트
            try:
                await asyncio.to_thread(update_post, post_id, content=current_draft)
                preview = current_draft[:300].replace("\n", " ").strip()
                await ctx.send(
                    f"✅ WP draft 업데이트 완료!\n"
                    f"```\n{preview}...\n```\n"
                    f"👉 전체 확인: {admin_link}"
                )
            except Exception as e:
                await ctx.send(f"WP 업데이트 실패: {e}")
            continue

        else:  # ✅ 확정
            break

    await finish_run(run_id, "success")
    await ctx.send(f"초안 확정했어요! WP에서 직접 발행해주세요.\n👉 {admin_link}")

    try:
        for entry in result.get("agent_tokens", []):
            await log_agent(run_id, entry["agent"], entry["input_tokens"],
                            entry["output_tokens"], entry["duration_sec"])
    except Exception:
        pass

    try:
        await log_post(
            run_id,
            post.get("id", 0),
            seo.get("title") or topic,
            result["keywords"][0] if result["keywords"] else "",
            seo.get("tags", [])
        )
    except Exception:
        pass

@bot.command(name="통계")
async def stats(ctx, arg: str = ""):
    if arg.isdigit():
        detail = await get_run_detail(int(arg))
        if not detail:
            await ctx.send(f"Run #{arg} 없어요.")
            return
        run = detail["run"]
        agents = detail["agents"]
        post = detail["post"]
        duration = ""
        if run["started_at"] and run["finished_at"]:
            from datetime import datetime
            s = datetime.fromisoformat(run["started_at"])
            e = datetime.fromisoformat(run["finished_at"])
            duration = f"{int((e - s).total_seconds())}초"
        cost = sum(calc_cost(a["agent"], a["input_tokens"] or 0, a["output_tokens"] or 0) for a in agents)
        msg = f"**🔍 Run #{run['id']} | {run['topic']}**\n"
        msg += f"상태: {run['status']} | 소요: {duration}\n"
        for a in agents:
            msg += f"`{a['agent']}` 입력 {a['input_tokens'] or 0}tok / 출력 {a['output_tokens'] or 0}tok / {a['duration_sec'] or 0}초\n"
        msg += f"💰 비용: ${cost:.4f}\n"
        if post:
            msg += f"📝 제목: {post['title']}\n키워드: {post['keywords']}"
        await ctx.send(msg)

    elif arg == "목록":
        runs = await get_run_list()
        if not runs:
            await ctx.send("기록이 없어요.")
            return
        msg = "**📋 실행 목록**\n"
        for r in runs:
            date = r["started_at"][:10] if r["started_at"] else "-"
            title = r["title"] or r["topic"]
            msg += f"`#{r['id']}` {title} | {r['status']} | {date} | ${r['cost']:.4f}\n"
        await ctx.send(msg)

    else:
        summary = await get_summary()
        status = summary["status"]
        tokens = summary["tokens"]
        msg = "**📊 누적 통계**\n"
        msg += f"총 실행: {sum(status.values())}회 (성공 {status.get('success', 0)} / 취소 {status.get('cancelled', 0)} / 실패 {status.get('fail', 0)})\n"
        msg += f"총 글: {summary['post_count']}개\n"
        for agent, t in tokens.items():
            msg += f"`{agent}` 입력 {t['input']:,}tok / 출력 {t['output']:,}tok\n"
        msg += f"💰 총 비용: ${summary['total_cost']:.4f}"
        await ctx.send(msg)


def run():
    bot.run(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    run()
