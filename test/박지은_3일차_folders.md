이 가이드는 제시된 프로젝트 구조를 계층형 아키텍처(Layered Architecture) 지향점에 맞춰 정리한 명세입니다. 이전 대화에서 진단한 구조적 결함(모델 정의 이원화)을 해결하는 최적화 구조를 반영하여 작성되었습니다.

---

## 1. 디렉터리별 역할 및 작성 파일 정의

전체 시스템은 **관심사 분리(Separation of Concerns)** 원칙에 따라 격리됩니다. 상위 계층은 하위 계층을 의존하지만, 하위 계층은 상위 계층을 알지 못해야 합니다.

| 디렉터리 경로 | 핵심 역할 | 작성해야 할 파일 내용 예시 |
| --- | --- | --- |
| **`app/core/`** | 시스템 전역 설정 및 인프라 제어 | `.env` 파싱 설정 파일, 데이터베이스 커넥션 풀(엔진 및 세션 팩토리) 생성, 공통 보안(JWT) 모듈 |
| **`app/models/`** | 데이터베이스 영속성(Persistence) 명세 | SQLAlchemy ORM 기반의 실제 DB 테이블 대응 클래스 정의 (예: `user.py`, `item.py`) 및 전체 모델 일괄 노출을 위한 `__init__.py` |
| **`app/schemas/`** | 데이터 입출력 및 유효성 검증 계층 | Pydantic 기반의 DTO(Data Transfer Object) 정의. Request용 검증 스키마, Response용 직렬화 스키마 분리 작성 |
| **`app/repositories/`** | 데이터 액세스 계층 (DAL) | 비즈니스 로직 없이 오직 데이터베이스에 직접 접근하여 CRUD(Create, Read, Update, Delete) 쿼리만 수행하는 클래스 |
| **`app/services/`** | 핵심 비즈니스 도메인 로직 계층 | 비즈니스 규칙 처리, 트랜잭션 단위 제어(`db.commit()`), 복수의 Repository 조합을 통한 비즈니스 목적 달성 |
| **`app/apis/`** | HTTP 엔드포인트 제어 계층 (Controller) | FastAPI 라우터 정의. HTTP 요청 접수 $\rightarrow$ Schema 검증 $\rightarrow$ Service 레이어 호출 $\rightarrow$ 결과 Schema 반환 |

---

## 2. 주요 설정 파일의 역할 정의

### `app/main.py`

애플리케이션의 엔트리 포인트(Entry Point)입니다. FastAPI 인스턴스를 생성하고 미들웨어(CORS, 로깅 등), 글로벌 익셉션 핸들러, 그리고 `app/apis/`에 정의된 라우터들을 최종적으로 통합 바인딩하는 역할을 합니다.

### `app/core/config.py`

시스템 환경변수 관리자입니다. 루트 레벨의 `.env` 파일에 기록된 문자열 데이터를 읽어와 파이썬 데이터 타입(int, str 등)으로 형변환 및 검증을 수행하고, 프로젝트 전역에서 사용할 고정 `settings` 객체를 노출합니다. (주로 `pydantic-settings` 라이브러리 활용)

### `pyproject.toml`

PEP 518/621 규격을 따르는 프로젝트의 현대적 통합 메타데이터 명세서입니다. 프로젝트 이름, 버전, 필요한 외부 라이브러리 의존성(Dependencies)뿐만 아니라 Ruff, Black, Pytest 등 개발 도구들의 설정까지 한 파일 내에서 통합 관리합니다.

### `uv.lock`

차세대 파이썬 패키지 매니저인 `uv`가 자동으로 관리하는 의존성 잠금(Lock) 파일입니다. 프로젝트에 설치된 모든 패키지와 그 하위 의존성들의 정확한 버전, 체크섬(Hash)을 기록하여 팀원 간 또는 운영 서버 배포 시 완벽히 동일한 실행 환경을 보장합니다. **(인위적 수정 금지)**

---

## 3. 데이터베이스 연결 설정 (`app/core/db/databases.py`)

순환 참조와 마이그레이션 누락을 방지하기 위해, 이 파일에서 **커넥션 설정과 상속용 `Base` 선언을 동시에 완료**합니다. (`app/core/db/models.py`는 제거합니다.)

```python
# app/core/db/databases.py
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# 1. 데이터베이스 엔진 생성 (settings 연동)
ENGINE = create_engine(
    settings.DATABASE_URL, 
    pool_pre_ping=True,  # 연결 유효성 선검증 옵션
    echo=False
)

# 2. 개별 요청(Request) 처리를 위한 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)

# 3. 모든 ORM 모델이 상속받을 전역 메타데이터 장부 (Base Class)
Base = declarative_base()

# 4. FastAPI Dependency Injection용 DB 세션 제네레이터
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # 요청 처리가 끝나면 반드시 커넥션 반환

```

---

## 4. SQLAlchemy 모델 작성 및 Alembic 마이그레이션 가이드

### ① ORM 모델 작성 (`app/models/`)

반드시 `app/core/db/databases.py`에 선언된 `Base`를 가져와 상속받아야 합니다.

```python
# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.db.databases import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

```

### ⚠️ 치명적 SPOF 방지: `app/models/__init__.py` 등록

새로운 모델 파일(예: `item.py`)을 만들 때마다 아래 파일에 반드시 명시적으로 import 해주어야 Alembic이 변경 사항을 추적할 수 있습니다.

```python
# app/models/__init__.py
from app.core.db.databases import Base
from app.models.user import User  # 반드시 임포트 구조 명시
# 새로운 모델 추가 시 여기에 지속적으로 추가

```

### ② Alembic 환경 설정 변경 (`alembic/env.py`)

Alembic이 메타데이터 장부를 정확히 바라보도록 상단 설정을 수정합니다.

```python
# alembic/env.py 상단 수정
from app.core.config import settings
from app.models import Base  # app/core/db/models가 아닌 통합 위치에서 import

# alembic.ini의 주소를 .env 기반 실시간 주소로 덮어쓰기
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# target_metadata를 우리 전역 장부로 교체
target_metadata = Base.metadata

```

### ③ 마이그레이션 명령어 실행 순서

터미널(프로젝트 루트 경로)에서 수행합니다.

1. **변경 사항 감지 및 스크립트 생성:**
```bash
uv run alembic revision --autogenerate -m "Create users table"

```


*수행 결과:* `alembic/versions/` 내부에 시간 기반 명명법을 가진 파이썬 마이그레이션 파일이 생성됩니다. 생성된 파일 내용을 육안으로 최종 검증하는 습관이 중요합니다.
2. **실제 데이터베이스에 반영:**
```bash
uv run alembic upgrade head

```



---

## 5. API 구현 흐름 (Data Flow Pattern)

하나의 기능이 작동하기 위해 데이터가 이동하는 표준 사이클은 다음과 같습니다.

```
[Client Request] 
       │
       ▼
 1. [app/apis/] ──────────────► (요청 접수 및 파라미터를 app/schemas/ 객체로 자동 검증)
       │
       ▼
 2. [app/services/] ──────────► (비즈니스 정책 수행, 필요 시 트랜잭션 관리)
       │
       ▼
 3. [app/repositories/] ──────► (SQLAlchemy 세션을 활용해 DB 데이터 제어)
       │
       ▼
 4. [Database] ───────────────► (I/O 수행 후 app/models/ 객체 형태로 데이터 반환)
       │
       ▼
 5. [app/services/ & apis/] ──► (ORM 모델 데이터를 클라이언트용 응답 app/schemas/로 변환/직렬화)
       │
       ▼
[Client Response (JSON)]

```

### 계층별 구현 체크리스트

1. **Schema 정의:** 클라이언트가 줄 데이터(`UserCreate`)와 서버가 나갈 데이터(`UserResponse`) 규격을 `app/schemas/`에 먼저 작성합니다.
2. **Repository 구현:** DB 쿼리를 수행하는 전담 메서드를 `app/repositories/`에 정의합니다.
3. **Service 구현:** Repository를 주입받아 실질적인 비즈니스 규칙(예: 이메일 중복 검사 등)을 수행하는 코드를 `app/services/`에 정의합니다.
4. **API Router 구현:** `app/apis/`에서 엔드포인트를 열고 디펜던시 인젝션(`Depends(get_db)`)을 통해 서비스를 호출하여 클라이언트에게 응답을 전송합니다.