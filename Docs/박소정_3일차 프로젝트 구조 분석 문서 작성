# 3일차 - 프로젝트 템플릿 뜯어보기

## 프로젝트 전체 구조

```bash
AH_health_web_development_assignment
├── README.md
├── alembic/
│   ├── README.md
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── alembic.ini
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── db/
│   │       ├── __init__.py
│   │       ├── databases.py
│   │       └── models.py
│   ├── apis/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   ├── media/
│   ├── static/
│   ├── templates/
│   │   └── index.html
│   ├── main.py
│   └── Dockerfile
├── 
├── docs/
├── .env
├── pyproject.toml
└── uv.lock
```

---

## 1. 각 디렉터리의 역할

### `app/core/`
프로젝트 전체에서 공통으로 사용하는 핵심 설정을 모아두는 폴더.
환경변수 설정, 데이터베이스 연결, 공통 유틸리티 등이 위치.

```python
# 작성하는 파일 예시
config.py        # 환경변수 로드 (DB 주소, JWT 시크릿 키 등)
db/databases.py  # DB 세션 생성 및 연결 관리
db/models.py     # 모든 모델이 상속받는 Base 클래스 정의
```

---

### `app/models/`
SQLAlchemy ORM을 사용하여 **데이터베이스 테이블을 Python 클래스로 정의**하는 폴더.
각 테이블마다 하나의 파일을 생성.

```python
# 작성하는 파일 예시
models/user.py      # users 테이블 정의
models/patient.py   # patients 테이블 정의
models/record.py    # medical_records 테이블 정의

# 예시 코드
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
```

---

### `app/repositories/`
**데이터베이스 쿼리(CRUD)를 전담**하는 폴더.
비즈니스 로직(service)과 DB 접근 코드를 분리하여 유지보수를 쉽게한다.

```python
# 작성하는 파일 예시
repositories/user_repository.py

# 예시 코드
async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
```

---

### `app/schemas/`
**API의 요청(Request) / 응답(Response) 데이터 형식을 Pydantic으로 정의**하는 폴더.
입력값 검증과 직렬화(Serialization)를 담당.

```python
# 작성하는 파일 예시
schemas/user_schema.py

# 예시 코드
class SignupRequest(BaseModel):
    email: str
    password: str
    name: str
    department: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str

    model_config = ConfigDict(from_attributes=True)
```

---

### `app/services/`
**비즈니스 로직을 처리**하는 폴더입니다.
라우터(apis)에서 요청을 받아 repository를 호출하고, 결과를 가공하여 반환.
JWT 발급, 비밀번호 해시, 권한 검사 등의 로직이 여기에 위치.

```python
# 작성하는 파일 예시
services/user_service.py

# 예시 코드
async def signup(db: AsyncSession, data: SignupRequest):
    existing = await user_repository.get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="이미 사용 중인 이메일입니다.")
    hashed_pw = hash_password(data.password)
    return await user_repository.create_user(db, data, hashed_pw)
```

---

### `app/apis/`
**FastAPI 라우터(엔드포인트)를 정의**하는 폴더.
HTTP 메서드(GET, POST, PATCH, DELETE)와 URL 경로를 지정하고,
요청을 받아 service 레이어로 전달한 뒤 응답을 반환.

```python
# 작성하는 파일 예시
apis/user_router.py

# 예시 코드
router = APIRouter(prefix="/api/v1/users", tags=["User"])

@router.post("/signup")
async def signup(data: SignupRequest, db: AsyncSession = Depends(get_db)):
    return await user_service.signup(db, data)
```

---

## 2. 각 파일의 역할

### `app/main.py`
FastAPI 앱을 생성하고, 각 기능별 라우터를 등록하는 **앱의 진입점(Entry Point)**.
미들웨어, static 파일 마운트, healthcheck 엔드포인트도 여기서 설정.

```python
app = FastAPI()
app.include_router(user_router)
app.include_router(patient_router)
```

---

### `app/core/config.py`
`.env` 파일에 저장된 **환경변수를 불러와 전역적으로 사용할 수 있게** 해주는 설정 파일.
pydantic-settings의 `BaseSettings`를 활용.

```python
# 예시
class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    JWT_SECRET_KEY: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
```

---

### `pyproject.toml`
프로젝트의 **메타정보와 의존성 패키지 목록**을 관리하는 파일.
`pip install` 대신 `uv add 패키지명` 으로 패키지를 추가하면 이 파일이 자동으로 업데이트 된다.

```toml
[project]
name = "ai-health-web-assignment"
dependencies = [
    "fastapi[standard]>=0.135.3",
    "sqlalchemy[asyncio]>=2.0.49",
    ...
]
```

---

### `uv.lock`
설치된 모든 패키지의 **정확한 버전을 고정**하는 파일.
팀원 모두가 `uv sync` 명령어 하나로 동일한 환경을 재현할 수 있게 해준다.
직접 수정하지 않으며, `uv add` / `uv sync` 시 자동으로 갱신.

---

## 3. 데이터베이스 연결 설정 (`app/core/db/databases.py`)

SQLAlchemy의 비동기 엔진을 사용하여 MySQL에 연결.

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

DATABASE_URL = (
    f"mysql+asyncmy://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# FastAPI Depends에서 사용하는 DB 세션 제공 함수
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

---

## 4. SQLAlchemy 모델 작성 및 Alembic 마이그레이션

### 모델 작성 순서

```
1. app/models/user.py 에 SQLAlchemy 모델 클래스 작성
2. alembic/env.py 에 모델 import 및 target_metadata 설정
3. 마이그레이션 파일 자동 생성
4. 데이터베이스에 적용
```

### 마이그레이션 명령어

```bash
# 1. 마이그레이션 파일 자동 생성 (모델 변경 감지)
uv run alembic revision --autogenerate -m "create users table"

# 2. 데이터베이스에 적용
uv run alembic upgrade head

# 3. 롤백 (이전 상태로 되돌리기)
uv run alembic downgrade -1
```

---

## 5. API 구현 흐름

클라이언트 요청이 처리되는 전체 흐름.

```
Client (HTTP 요청)
    ↓
[apis/user_router.py]       # URL 라우팅, 요청 수신
    ↓
[schemas/user_schema.py]    # 요청 데이터 유효성 검증 (Pydantic)
    ↓
[services/user_service.py]  # 비즈니스 로직 처리 (JWT 발급, 권한 체크 등)
    ↓
[repositories/user_repository.py]  # DB 쿼리 실행 (SQLAlchemy)
    ↓
[models/user.py]            # DB 테이블 매핑
    ↓
Database (MySQL)
    ↓
응답 반환 (JSON)
```

### 계층별 책임 요약

| 계층 | 폴더 | 책임 |
|------|------|------|
| Router | `apis/` | URL 매핑, 요청 수신 및 응답 반환 |
| Schema | `schemas/` | 입출력 데이터 검증 및 직렬화 |
| Service | `services/` | 비즈니스 로직, 예외 처리 |
| Repository | `repositories/` | DB CRUD 쿼리 |
| Model | `models/` | DB 테이블 구조 정의 |

---

## 참고 자료

- https://devocean.sk.com/blog/techBoardDetail.do?ID=166993&boardType=techBlog
- https://brotherdan.tistory.com/40
- https://dev.to/mohammad222pr/structuring-a-fastapi-project-best-practices-53l6
