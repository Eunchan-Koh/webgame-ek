# CLAUDE.md

## 작업 규칙

- 사용자가 말한 내용 이상의 내용을 가정해서 적거나 만들지 말 것.
  - 단, 사용자가 허락한 경우에는 가정해서 채워도 됨.
- 제안할 거리가 있으면 항상 제안하고, "제안 (미확정)"으로 표시해 사용자가 정한 내용과 구분할 것.

## 프로젝트

- 링크만 있으면 누구나 들어와서 할 수 있는 간단한 웹 물건 찾기 게임 (io 사이트 게임 같은 느낌).
- 자세한 요구사항은 PRD에 있다: https://claude.ai/artifact/T8DXgQjbWPXV8Guj8qaHtR
- 개발 방식: MVP를 먼저 만들고, 그 위에 기능을 덧붙여 나간다.
- 배포까지 고려해서 만든다.

## 개발 팀 (MVP)

- `.claude/agents/`의 backend, frontend, reviewer agent를 쓴다. orchestrator는 아직 두지 않고 메인 세션이 일을 나눠 맡긴다.
- agent는 PRD를 직접 읽지 못할 수 있으므로, 맡길 때 필요한 PRD 내용을 지시에 넣어 준다.
- 본격 개발 때는 agent와 orchestrator로 팀을 만들어 돌릴 예정이다.

## 기술 스택

- DB: PostgreSQL
- Cache: Redis
- Backend: Python + FastAPI
- Frontend: React + Canvas (필요하면 PixiJS 추가)
- 배포: Docker. 배포 대상은 AWS Lightsail(서버) + Cloudflare(도메인). 실제 배포는 하지 않고, 이 환경에 배포할 것을 기준으로 만든다. 서버 한 대에 docker-compose로 전체(프론트엔드, 백엔드, PostgreSQL, Redis)를 띄우고 Nginx로 도메인·HTTPS 연결. 로컬에서도 `docker compose up` 한 번으로 전체가 떠야 함.
- 정답 판정과 점수 계산은 서버가 한다. 아이템 위치는 그리기용으로 클라이언트에 보내고, 클라이언트는 클릭 좌표만 서버에 보낸다.
