"""
3일차

Step 1. 프로젝트 구조 분석
Step 2. DB 모델 작성 및 마이그레이션

작성자 : 팀명
작성일 : 2026-06-10
"""

# ==================================================
# 1. 디렉터리 역할
# ==================================================

PROJECT_STRUCTURE = {
    "app/core": """
프로젝트의 핵심 설정을 관리하는 영역

주요 역할
- 환경 변수 관리(.env)
- 데이터베이스 연결 설정
- 공통 설정 관리
- 보안 설정 관리

예시 파일
- config.py
- db/databases.py
""",

    "app/models": """
데이터베이스 테이블 구조 정의

주요 역할
- SQLAlchemy ORM 모델 작성
- 테이블 생성 구조 정의
- 테이블 간 관계(Relationship) 정의
""",

    "app/repositories": """
데이터베이스 접근 계층

주요 역할
- CRUD(Create, Read, Update, Delete)
- SQL 실행
- DB 데이터 조회 및 저장
""",

    "app/schemas": """
API 요청 및 응답 데이터 검증

주요 역할
- Pydantic 모델 정의
- 요청 데이터 검증
- 응답 형식 통일
""",

    "app/services": """
비즈니스 로직 처리 계층

주요 역할
- 회원가입
- 로그인
- 건강 정보 처리
- Repository 호출
""",

    "app/apis": """
API 엔드포인트 정의

주요 역할
- URL 관리
- 요청 수신
- Service 호출
- 응답 반환
"""
}

# ==================================================
# 2. 주요 파일 역할
# ==================================================

FILES_DESCRIPTION = {
    "app/main.py": """
프로젝트 실행 시작점

주요 역할
- FastAPI 객체 생성
- Router 등록
- 서버 실행
""",

    "app/core/config.py": """
환경 변수 및 설정 관리

주요 역할
- DATABASE_URL
- SECRET_KEY
- API_KEY
- 기타 설정값 로드
""",

    "pyproject.toml": """
프로젝트 의존성 관리 파일

주요 역할
- Python 버전 설정
- 라이브러리 관리
- 프로젝트 정보 관리
""",

    "uv.lock": """
설치 패키지 버전 고정 파일

주요 역할
- 동일한 개발 환경 유지
- 패키지 버전 충돌 방지
"""
}

# ==================================================
# 3. 데이터베이스 연결 설정
# ==================================================

DATABASE_SETTING = """
파일 위치

app/core/db/databases.py

주요 역할

1. Engine 생성
2. Session 생성
3. Database 연결 관리

예시

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
"""

# ==================================================
# 4. SQLAlchemy + Alembic 사용 방법
# ==================================================

SQLALCHEMY_AND_ALEMBIC = """
1. SQLAlchemy 모델 작성

예시

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)

------------------------------------------------

2. 마이그레이션 생성

명령어

alembic revision --autogenerate -m "create user table"

------------------------------------------------

3. 마이그레이션 적용

명령어

alembic upgrade head

------------------------------------------------

4. DB 확인

DBeaver
DataGrip
TablePlus

등을 이용하여 테이블 생성 여부 확인
"""

# ==================================================
# 5. API 구현 흐름
# ==================================================

API_FLOW = """
사용자 요청
    ↓
API Layer (app/apis)
    ↓
Schema Validation (app/schemas)
    ↓
Service Layer (app/services)
    ↓
Repository Layer (app/repositories)
    ↓
Database

예시

POST /users
    ↓
UserCreate Schema
    ↓
UserService
    ↓
UserRepository
    ↓
Database 저장
"""

# ==================================================
# Step 2. DB 모델 작성
# ==================================================

STEP2_DB_MODEL = """
1. ERD 확인

https://dbdiagram.io/

------------------------------------------------

2. 모델 작성

예시 파일

app/models/user.py
app/models/exercise.py
app/models/health_record.py

------------------------------------------------

3. 관계(Relationship) 설정

예시

user = relationship("User")

------------------------------------------------

4. 마이그레이션 생성

alembic revision --autogenerate -m "create tables"

------------------------------------------------

5. DB 반영

alembic upgrade head

------------------------------------------------

6. DB Viewer 확인

생성된 테이블 확인

------------------------------------------------

7. docs 작성

docs/3일차_db_migration.md

작성 내용
- 실행 명령어
- 실행 결과
- DB Viewer 캡처 이미지
"""

# ==================================================
# 제출 체크리스트
# ==================================================

CHECK_LIST = [
    "프로젝트 구조 분석 완료",
    "모델 작성 완료",
    "Alembic Migration 생성 완료",
    "Database 반영 완료",
    "DB Viewer 확인 완료",
    "docs/3일차_db_migration.md 작성 완료",
    "Pull Request 생성",
    "팀원 승인",
    "main 또는 develop 브랜치 머지 완료"
]

print("3일차 folders 정리 완료")