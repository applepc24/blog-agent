# 눕고싶은 취준생의 생존일지 - 블로그 자동화 에이전트

비전공자 데이터 엔지니어 취준생이 운영하는 블로그의 콘텐츠 생산을 자동화하는 멀티 에이전트 시스템.

## 구조

```
편집장 (Claude Opus)
  ↕ 디스코드
┌─────────────────────────────────┐
│  리서처       라이터      SEO분석가  │
│ (Haiku)    (Sonnet)    (Haiku)  │
│ 키워드리서치  초안작성    제목/태그   │
└─────────────────────────────────┘
       ↕
  장독대 (SQLite)
       ↕
  WordPress REST API
```

## 기술 스택

- Python 3.12
- LangGraph (Supervisor 패턴)
- Claude API (Anthropic)
- discord.py
- SQLite
- WordPress REST API
- Naver DataLab + pytrends (키워드 트렌드)

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

서버에서 자동 실행 (systemd):
```bash
sudo systemctl start blog-agent
sudo systemctl status blog-agent
```

## 디스코드 명령어

| 명령어 | 설명 |
|--------|------|
| `!글쓰기 주제` | 주제로 블로그 글 자동 작성 후 WordPress 업로드 |
| `!글감 내용` | 장독대에 글감 저장 |
| `!장독대` | 저장된 글감 목록 조회 |
| `!편집장 말` | 편집장(Opus)과 대화 |
| `!도움말` | 명령어 목록 |

## 글 생성 흐름

1. `!글쓰기 주제` 입력
2. 리서처: 네이버/구글 트렌드 기반 키워드 리서치
3. 라이터: SEO 최적화 초안 작성
4. SEO분석가: 제목/메타디스크립션/태그 생성
5. 디스코드로 미리보기 전송
6. 확인 후 WordPress draft로 자동 업로드

## 블로그

- [comeandlook.site](https://comeandlook.site)
