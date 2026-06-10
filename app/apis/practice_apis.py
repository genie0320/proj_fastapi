import re
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator

router = APIRouter(prefix="/practice_api", tags=["Practice"])

# 초기 데이터셋
user_list = [
    {
        "id": 1,
        "name": "홍길동",
        "age": 24,
        "email": "gildong24@example.com",
        "password": "Password1234!!",
    },
    {
        "id": 2,
        "name": "장문복",
        "age": 21,
        "email": "moonluck12@example.com",
        "password": "Check1321!",
    },
    {
        "id": 3,
        "name": "임우진",
        "age": 31,
        "email": "limousine33@example.com",
        "password": "lwsPAssword12@",
    },
]

# 정규표현식 컴파일 (이메일 및 패스워드 복잡도)
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,20}$"
)


# --- Pydantic Schemas ---
class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    email: str


class UserCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=10)
    age: int = Field(..., ge=14)
    email: str = Field(..., max_length=30)
    password: str = Field(...)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not EMAIL_REGEX.match(v):
            raise ValueError("올바른 이메일 형식이 아닙니다.")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not PASSWORD_REGEX.match(v):
            raise ValueError(
                "비밀번호는 대소문자, 특수문자가 각 1개씩 포함된 8~20자여야 합니다."
            )
        return v


class UserUpdateRequest(BaseModel):
    age: int | None = Field(None, ge=14)
    email: str | None = Field(None, max_length=30)
    password: str | None = Field(None)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str | None) -> str | None:
        if v is not None and not EMAIL_REGEX.match(v):
            raise ValueError("올바른 이메일 형식이 아닙니다.")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str | None) -> str | None:
        if v is not None and not PASSWORD_REGEX.match(v):
            raise ValueError(
                "비밀번호는 대소문자, 특수문자가 각 1개씩 포함된 8~20자여야 합니다."
            )
        return v


# --- API Endpoints ---


# 1. 모든 회원 정보 목록 조회 API
@router.get("/users", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
def get_all_users():
    return user_list


# 2. 특정 회원 정보 조회 API (Path Parameter)
@router.get(
    "/users/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK
)
def get_user_by_id(user_id: int):
    for user in user_list:
        if user["id"] == user_id:
            return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="해당 ID의 회원을 찾을 수 없습니다.",
    )


# 3. 회원 정보 추가 API (Request Body & Validation)
@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(request_data: UserCreateRequest):
    # 이메일 중복 체크
    if any(user["email"] == request_data.email for user in user_list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 이메일입니다.",
        )

    # Auto-increment ID 계산
    next_id = max(user["id"] for user in user_list) + 1 if user_list else 1

    new_user = {
        "id": next_id,
        "name": request_data.name,
        "age": request_data.age,
        "email": request_data.email,
        "password": request_data.password,
    }
    user_list.append(new_user)
    return new_user


# 4. 회원 정보 수정 API (Partial Update & Payload Check)
@router.patch(
    "/users/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK
)
def update_user(user_id: int, request_data: UserUpdateRequest):
    # 400 Bad Request: 모든 항목이 입력되지 않은 경우 (전부 None인 경우) 확인
    update_dict = request_data.model_dump(exclude_unset=True)
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수정할 필드가 최소 하나 이상 입력되어야 합니다.",
        )

    # 대상 유저 검색
    target_user = None
    for user in user_list:
        if user["id"] == user_id:
            target_user = user
            break

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 ID의 회원을 찾을 수 없습니다.",
        )

    # 데이터 업데이트 실행
    for key, value in update_dict.items():
        target_user[key] = value

    return target_user


# 5. 특정 회원 정보 삭제 API
@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    for index, user in enumerate(user_list):
        if user["id"] == user_id:
            user_list.pop(index)
            return  # 204 No Content는 본문을 반환하지 않음

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="해당 ID의 회원을 찾을 수 없습니다.",
    )
