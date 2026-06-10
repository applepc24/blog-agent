# 진행 상황

## 완료
- 1~5단계: 디스코드 봇 + 편집장 + 장독대 + LangGraph 워크플로우 + 파이프라인 연결
- 6단계: WordPress Docker 세팅 + REST API + 마크다운→HTML 자동 업로드
- 7단계: 리서처 키워드 시스템 (네이버 데이터랩 + pytrends, 롱테일 변환)
- 8단계: 라이터/리서처 프롬프트 품질 개선
- 9단계: 배포 (comeandlook.site, Nginx, Let's Encrypt SSL)
- SEO 에이전트 개선 (draft 8000자, 프롬프트 보강, JSON 파싱 안전화, 제목 점수화)
- 리서처 개선 (0점 시 자동 재시도 → 그래도 0점이면 디스코드 경고 후 확인)
- 블로그 첫 글 게시 완료
- 서버 배포: 디스코드 봇 Linux 서버에서 systemd 서비스로 24시간 실행
- SEO 제목 스타일 다양화 (패턴 반복 방지)
- 리서처 IndexError 버그 수정
- GitHub Actions CI/CD 구축 (push 시 서버 자동 배포) ✅
- 테마 변경 (Twenty Twenty-Five → Astra)
- 소개 페이지 작성
- 카테고리 정리 (개발/데이터, 다이어트/건강)
- RankMath SEO 플러그인 설치
- Google Search Console 등록 + 사이트맵 제출
- 네이버 서치어드바이저 등록 + 사이트맵 제출

## 다음
- 글 10~20개 작성하며 시스템 안정화
- **데이터 레이어 구축**: runs/agent_logs/posts/keywords 테이블 설계 + 에이전트 로깅 연결 (포트폴리오)
- **편집장 모델 변경**: Opus → Sonnet (대화/검토는 Sonnet으로 충분)
- Google Search Console 데이터 확인 (글 10개 이후)
- 개인정보처리방침 페이지 작성
- 애드센스 신청 (글 20~30개 이후)
- cron 자동화
- **조율자(coordinator) 구현**: Opus 사용, 주간 리포트 해석 + 다음 글 방향 전략 제안 (GSC 연결 후)
- 벡터 DB 장기 기억 (글 100개 이후)

## 아이디어 (미구현)
- **라이터 자기개선 루프**: Search Console에서 방문률 상위 글을 추출 → 라이터 에이전트가 제목 패턴/글 구조/도입부 스타일/검색 의도 유형 분석 → Skill 문서 자동 생성 후 DB 저장 → 다음 글 작성 시 컨텍스트에 주입. Search Console 연결 시점(글 10개 이후)에 같이 구현 예정. (Hermes Agent의 Skill 개념 참고)

## 메모
- 블로그 (외부): https://comeandlook.site
- 조율자(coordinator) 에이전트는 규모 커지면 추가 예정
- 서버 접속 정보는 LOCAL_NOTES.md 참고
