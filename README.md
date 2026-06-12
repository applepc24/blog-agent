# 눕고싶은 취준생의 생존일지 - 블로그 자동화 에이전트

비전공자 데이터 엔지니어 취준생이 운영하는 블로그([comeandlook.site](https://comeandlook.site))의 콘텐츠 생산을 자동화하는 멀티 에이전트 시스템.

주제: 개발/데이터 (70%) + 다이어트/건강 (30%)

## 구조

```
편집장 (Claude Opus)  ←→  디스코드 봇  ←→  준석
                              ↕
              [LangGraph Supervisor - workflow.py]
                              ↕
        ┌─────────────────────────────────────┐
        │  리서처 (Haiku)    라이터 (Sonnet)   SEO분석가 (Haiku)  │
        │  네이버/구글 키워드  초안 작성          제목/메타/태그     │
        └─────────────────────────────────────┘
                              ↕
                       장독대 (SQLite)
                              ↕
                    WordPress REST API
```

## 기술 스택

- Python 3.11
- LangGraph (Supervisor 패턴)
- Claude API — Opus / Sonnet / Haiku
- discord.py
- SQLite (장독대 + 실행 로그)
- WordPress REST API + RankMath SEO
- Naver DataLab + pytrends (키워드 트렌드)

## 인프라

- 개인 Linux 미니 PC (24시간 운영)
- systemd 서비스로 봇 실행
- GitHub Actions CI/CD — push 시 서버 자동 배포

## 설치

```bash
git clone https://github.com/applepc24/blog-agent.git
cd blog-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

`.env` 파일 생성:
```
ANTHROPIC_API_KEY=
DISCORD_BOT_TOKEN=
DISCORD_CHANNEL_ID=
WP_URL=
WP_USER=
WP_APP_PASSWORD=
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=
```

## 실행

```bash
source venv/bin/activate
python3 -m discord_bot.bot
```

서버 (systemd):
```bash
sudo systemctl start blog-agent
sudo systemctl status blog-agent
```

## 디스코드 명령어

| 명령어 | 설명 |
|--------|------|
| `!글쓰기 주제` | 주제로 블로그 글 자동 작성 |
| `!글쓰기` | 장독대 목록 표시 후 번호 선택 |
| `!글감 내용` | 장독대에 글감 저장 |
| `!장독대` | 저장된 글감 목록 조회 |
| `!편집장 말` | 편집장(Opus)과 대화 |
| `!통계` | 누적 토큰/비용 요약 |
| `!통계 목록` | 글별 실행 목록 |
| `!통계 N` | 특정 실행 상세 |
| `!도움말` | 명령어 목록 |

## 글 생성 흐름

```
1. !글쓰기 주제 입력 (또는 장독대에서 선택)
2. 경험/참고 내용 입력 (없으면 "없음")
3. 리서처: 네이버/구글 기반 롱테일 키워드 리서치
4. 라이터: 키워드 + 경험 녹인 SEO 최적화 초안 작성
5. SEO분석가: 제목/메타디스크립션/태그/포커스 키워드 생성
6. 디스코드로 미리보기 + SEO 결과 전송
7. ✅ 업로드 / ✏️ 수정 요청 / ❌ 취소
   - ✏️: 수정 내용 입력 → 라이터가 재작성 → 다시 확인 (반복 가능)
8. WordPress draft로 자동 업로드 + RankMath 포커스 키워드 전송
```
