# webgame-ek

링크만 있으면 누구나 들어와서 할 수 있는 간단한 웹 물건 찾기 게임.

어두운 화면에서 마우스 커서 주변만 손전등처럼 밝아지고, 화면 오른쪽에 표시된 아이템 5개를 제한 시간 10분 안에 찾는다.

## 현재 상태

MVP: 게스트 플레이, 서버 정답 판정, 점수 계산. 계정·로그인·랭킹은 이후 추가 예정.

- 점수: 찾은 아이템 1개당 100점 + 남은 시간 1초당 1점
- 시간 초과 시 그때까지 찾은 아이템의 기본 점수만 인정
- 정답 판정과 점수 계산은 서버에서 한다

## 기술 스택

| 영역 | 사용 |
| --- | --- |
| Frontend | React + TypeScript + Canvas (Vite), Nginx |
| Backend | Python + FastAPI |
| DB / Cache | PostgreSQL / Redis |
| 실행 | Docker Compose |

## 실행

Docker가 필요하다.

```bash
docker compose up --build
```

http://localhost:8080 에서 플레이. 종료는 `docker compose down`.

## 개발

```bash
# 백엔드 테스트
cd backend
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q

# 프론트엔드 개발 서버 (백엔드가 localhost:8000에 떠 있어야 함)
cd frontend
npm install
npm run dev
```

## 구조

```
backend/              FastAPI 서버 (설계: backend/DESIGN.md)
frontend/             React 앱, Nginx 설정
docker-compose.yml    전체 스택 (web, backend, db, redis)
```
