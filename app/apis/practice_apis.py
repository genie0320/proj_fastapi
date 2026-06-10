import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional

router = APIRouter(prefix="/practice_api", tags=["Practice API"])

# ── 초기 데이터 ──────────────────────────────────────────────
user_list = [
    {
        "id": 1,
        "name": "홍길동",
        "age": 24,
        "email": "gildong24@example.com",
        "password": "Password1234!!"
    },
    {
        "id": 2,
        "name": "장문복",
        "age": 21,
        "email": "moonluck12@example.com",
        "password": "Check1321!"
    },
    {
        "id": 3,
        "name": "임우진",
        "age": 31,
        "email": "limousine33@example.com",
        "password": "lwsPAssword12@"
    }
]


# ── 검증 헬퍼 함수 ────────────────────────────────────────────
def validate_password(password: str) -> str:
    """비밀번호: 대문자/소문자/특수문자 각 1개 이상, 8~20자"""
    if not (8 <= len(password) <= 20):
        raise ValueError("비밀번호는 8자 이상 20자 이하여야 합니다.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("비밀번호에 대문자가 1개 이상 포함되어야 합니다.")
    if not re.search(r"[a-z]", password):
        raise ValueError("비밀번호에 소문자가 1개 이상 포함되어야 합니다.")
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        raise ValueError("비밀번호에 특수문자가 1개 이상 포함되어야 합니다.")
    return password


def validate_email_format(email: str) -> str:
    """이메일: 정규표현식 형식 검증, 최대 30자"""
    if len(email) > 30:
        raise ValueError("이메일은 최대 30자까지 입력 가능합니다.")
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        raise ValueError("올바른 이메일 형식이 아닙니다.")
    return email


# ── Pydantic 스키마 ───────────────────────────────────────────
class UserCreate(BaseModel):
    name: str
    age: int
    email: str
    password: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not (2 <= len(v) <= 10):
            raise ValueError("이름은 2글자 이상 10글자 이하여야 합니다.")
        return v

    @field_validator("age")
    @classmethod
    def validate_age(cls, v):
        if v < 14:
            raise ValueError("나이는 14세 이상이어야 합니다.")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        return validate_email_format(v)

    @field_validator("password")
    @classmethod
    def validate_pw(cls, v):
        return validate_password(v)


class UserUpdate(BaseModel):
    age: Optional[int] = None
    email: Optional[str] = None
    password: Optional[str] = None

    @field_validator("age")
    @classmethod
    def validate_age(cls, v):
        if v is not None and v < 14:
            raise ValueError("나이는 14세 이상이어야 합니다.")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if v is not None:
            return validate_email_format(v)
        return v

    @field_validator("password")
    @classmethod
    def validate_pw(cls, v):
        if v is not None:
            return validate_password(v)
        return v


# ── API 1: 전체 회원 목록 조회 (GET) ─────────────────────────
@router.get("/users", summary="전체 회원 목록 조회")
def get_users():
    return [
        {"id": u["id"], "name": u["name"], "age": u["age"], "email": u["email"]}
        for u in user_list
    ]


# ── API 2: 특정 회원 조회 (GET) ───────────────────────────────
@router.get("/users/{user_id}", summary="특정 회원 조회")
def get_user(user_id: int):
    for user in user_list:
        if user["id"] == user_id:
            return {"id": user["id"], "name": user["name"], "age": user["age"], "email": user["email"]}
    raise HTTPException(status_code=404, detail="해당 id의 회원을 찾을 수 없습니다.")


# ── API 3: 회원 추가 (POST) ───────────────────────────────────
@router.post("/users", summary="회원 추가", status_code=201)
def create_user(user: UserCreate):
    # 이메일 중복 체크
    for u in user_list:
        if u["email"] == user.email:
            raise HTTPException(status_code=400, detail="이미 사용 중인 이메일입니다.")

    new_id = max(u["id"] for u in user_list) + 1
    new_user = {
        "id": new_id,
        "name": user.name,
        "age": user.age,
        "email": user.email,
        "password": user.password
    }
    user_list.append(new_user)
    return {"message": "회원이 성공적으로 추가되었습니다.", "id": new_id}


# ── API 4: 회원 정보 수정 (PATCH) ────────────────────────────
@router.patch("/users/{user_id}", summary="회원 정보 수정")
def update_user(user_id: int, user_update: UserUpdate):
    # 모든 항목이 None인 경우 400 반환
    if user_update.age is None and user_update.email is None and user_update.password is None:
        raise HTTPException(status_code=400, detail="수정할 항목을 1개 이상 입력해주세요.")

    for user in user_list:
        if user["id"] == user_id:
            if user_update.age is not None:
                user["age"] = user_update.age
            if user_update.email is not None:
                user["email"] = user_update.email
            if user_update.password is not None:
                user["password"] = user_update.password
            return {"message": "회원 정보가 성공적으로 수정되었습니다."}

    raise HTTPException(status_code=404, detail="해당 id의 회원을 찾을 수 없습니다.")


# ── API 5: 회원 삭제 (DELETE) ────────────────────────────────
@router.delete("/users/{user_id}", summary="회원 삭제")
def delete_user(user_id: int):
    for i, user in enumerate(user_list):
        if user["id"] == user_id:
            user_list.pop(i)
            return {"message": "회원이 성공적으로 삭제되었습니다."}

    raise HTTPException(status_code=404, detail="해당 id의 회원을 찾을 수 없습니다.")
