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

## 다음
- 글 10~20개 작성하며 시스템 안정화
- **데이터 레이어 구축**: runs/agent_logs/posts/keywords 테이블 설계 + 에이전트 로깅 연결 (포트폴리오)
- Google Search Console 등록 (글 10개 이후)
- 소개 페이지 + 개인정보처리방침 페이지 작성
- 애드센스 신청 (글 20~30개 이후)
- cron 자동화
- GitHub Actions CI/CD (코드 push 시 서버 자동 배포)
- 벡터 DB 장기 기억 (글 100개 이후)

## 메모
- WordPress: Linux 개인 서버 도커로 운영 중
  - 블로그 (내부): http://172.30.1.55:8080
  - 어드민 (내부): http://172.30.1.55:8080/wp-admin
  - 블로그 (외부): https://comeandlook.site
  - 어드민 (외부): https://comeandlook.site/wp-admin
  - 서버 접속: ssh junseok@172.30.1.55
  - MySQL 접속: docker exec -it wordpress-db mysql -u root -p (비밀번호: rootpassword)
- 맥 로컬 접속 시 Firefox 사용 (Chrome/Safari는 Private Network Access 정책으로 차단)
- 조율자(coordinator) 에이전트는 규모 커지면 추가 예정
- git 미적용 상태
