# blog-agent

![Python](https://img.shields.io/badge/Python-3.11-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-Supervisor-green)
![Claude](https://img.shields.io/badge/Claude-Opus%20%7C%20Sonnet%20%7C%20Haiku-purple)
![Discord](https://img.shields.io/badge/Interface-Discord-5865F2)
![Deploy](https://img.shields.io/badge/Deploy-GitHub%20Actions-black)

Discord 봇을 인터페이스로 사용하는 블로그 콘텐츠 자동화 멀티에이전트 시스템.  
키워드 리서치 → SEO 초안 작성 → WordPress 업로드까지 자동화, Human-in-the-loop 구조로 최종 확인은 사람이 담당.

**Live**: [comeandlook.site](https://comeandlook.site)

---

## Architecture

```
User (Discord)
     ↕
편집장 (Claude Opus)         # 주제 선정, 최종 검토, 호출 최소화
     ↕
LangGraph Supervisor
     ↕
┌──────────────────────────────────────────────┐
│  리서처 (Haiku)   라이터 (Sonnet)   SEO분석가 (Haiku)  │
│  키워드 트렌드     초안 8000자        제목 점수화        │
│  롱테일 변환       경험 단락 정제     메타/태그/키워드    │
└──────────────────────────────────────────────┘
     ↕                             ↕
장독대 (SQLite)           WordPress REST API
                          + RankMath SEO
```

**모델 비용 전략**: 반복 작업(리서치·SEO)은 Haiku, 글 품질이 중요한 작성은 Sonnet, 최종 판단만 Opus — 불필요한 Opus 호출 최소화.

---

## Features

- **키워드 리서치**: 네이버 데이터랩 + pytrends 기반 롱테일 키워드 자동 선정. 검색량 0점 시 재시도 → 그래도 낮으면 Discord 경고
- **장독대**: 일상에서 떠오른 글감을 Discord 자연어로 저장 (SQLite), `!글쓰기` 시 우선 활용
- **Human-in-the-loop**: 초안 완성 후 WP draft로 업로드 → 관리자 링크 공유 → 전체 글 확인 후 ✅/✏️/❌
- **수정 루프**: ✏️ 누르면 수정 요청 입력 → 라이터 재작성 → WP draft 자동 업데이트 반복
- **데이터 레이어**: 에이전트별 토큰·비용·소요시간 로깅, `!통계` 명령어로 조회

---

## Tech Stack

| 분류 | 기술 |
|------|------|
| Language | Python 3.11 |
| Agent Framework | LangGraph (Supervisor 패턴) |
| LLM | Anthropic Claude API (Opus / Sonnet / Haiku) |
| Interface | discord.py |
| Database | SQLite |
| External API | WordPress REST API, RankMath, Naver DataLab, pytrends |
| Infra | Linux (개인 서버), systemd, Nginx, Let's Encrypt |
| CI/CD | GitHub Actions |

---

## Workflow

```
1. !글쓰기 [주제]
   └─ 주제 없으면 장독대 목록 표시 → 번호 선택
2. 경험/참고 내용 입력 (없으면 "없음")
3. 리서처: 롱테일 키워드 리서치
4. 라이터: SEO 최적화 초안 작성
5. SEO분석가: 제목 / 메타디스크립션 / 태그 / 포커스 키워드 생성
6. WordPress draft 자동 업로드 → 관리자 링크 Discord 공유
7. 전체 글 읽고 결정 (30분 대기)
   ✅ 확정  →  WP에서 직접 발행
   ✏️ 수정  →  라이터 재작성 → WP draft 업데이트 → 반복
   ❌ 삭제  →  WP draft 삭제
```

---

## Progress

| 단계 | 내용 | 상태 |
|------|------|------|
| 1–5 | 디스코드 봇 + 편집장 + 장독대 + LangGraph 파이프라인 | ✅ |
| 6 | WordPress REST API + 서버 배포 | ✅ |
| 7 | 네이버 데이터랩 + pytrends 키워드 리서치 | ✅ |
| 8 | 데이터 레이어 (토큰/비용 로깅, `!통계`) | ✅ |
| 9 | GitHub Actions CI/CD + systemd 배포 | ✅ |
| 10 | 초안 수정 루프 + WP draft 확인 플로우 | ✅ |
| — | 글 게시 | ✅ 10개 |
| Next | 글 30개 달성 후 애드센스 신청 | 🔲 |
| Next | Google Search Console 피드백 루프 | 🔲 |
| Future | 조율자(coordinator) 에이전트 + 주간 리포트 | 🔲 |
| Future | 라이터 자기개선 루프 (상위 글 패턴 → Skill 문서 → 컨텍스트 주입) | 🔲 |

---

## Installation

```bash
git clone https://github.com/applepc24/blog-agent.git
cd blog-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

`.env`:
```
ANTHROPIC_API_KEY=
DISCORD_BOT_TOKEN=
DISCORD_CHANNEL_ID=
WP_URL=
WP_USERNAME=
WP_APP_PASSWORD=
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=
```

```bash
python3 -m discord_bot.bot
```

---

## Commands

| 명령어 | 설명 |
|--------|------|
| `!글쓰기 [주제]` | 블로그 글 자동 작성 (주제 생략 시 장독대에서 선택) |
| `!글감 내용` | 장독대에 글감 저장 |
| `!장독대` | 저장된 글감 목록 조회 |
| `!편집장 말` | 편집장(Opus)과 대화 |
| `!통계` | 누적 토큰/비용 요약 |
| `!통계 목록` | 글별 실행 목록 |
| `!통계 N` | 특정 실행 상세 |
