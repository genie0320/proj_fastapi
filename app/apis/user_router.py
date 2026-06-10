from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import RoleEnum, User
from app.core.db.databases import async_get_db
from app.core.security import REFRESH_TOKEN_EXPIRE_DAYS, decode_token
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import (
    MessageResponse,
    TokenResponse,
    UserLoginRequest,
    UserPasswordChangeRequest,
    UserResponse,
    UserRoleUpdateRequest,
    UserSignupRequest,
    UserUpdateRequest,
)
from app.services.user_service import UserService


router = APIRouter(prefix="/api/v1/users", tags=["User"])
security = HTTPBearer()


def get_user_service(db: AsyncSession = Depends(async_get_db)) -> UserService:
    return UserService(UserRepository(db))


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    service: UserService = Depends(get_user_service),
) -> User:
    payload = decode_token(credentials.credentials)
    return await service.get_user_or_404(int(payload["sub"]))


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != RoleEnum.ADMIN:
        from fastapi import HTTPException

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="관리자 권한이 필요합니다.")
    return current_user


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="회원가입")
async def signup(
    request: UserSignupRequest,
    service: UserService = Depends(get_user_service),
) -> User:
    return await service.signup(request)


@router.post("/login", response_model=TokenResponse, summary="로그인")
async def login(
    request: UserLoginRequest,
    response: Response,
    service: UserService = Depends(get_user_service),
) -> TokenResponse:
    token_response, refresh_token = await service.login(request)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="lax",
    )
    return token_response


@router.post("/logout", response_model=MessageResponse, summary="로그아웃")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    response.delete_cookie("refresh_token")
    return MessageResponse(message="로그아웃되었습니다.")


@router.get("", response_model=list[UserResponse], summary="회원 목록 조회(Admin)")
async def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    service: UserService = Depends(get_user_service),
    current_admin: User = Depends(get_current_admin),
) -> list[User]:
    return await service.list_users(skip=skip, limit=limit)


@router.patch("/{user_id}/role", response_model=UserResponse, summary="회원 권한 변경(Admin)")
async def update_user_role(
    user_id: int,
    request: UserRoleUpdateRequest,
    service: UserService = Depends(get_user_service),
    current_admin: User = Depends(get_current_admin),
) -> User:
    return await service.update_role(user_id, request.role)


@router.get("/me", response_model=UserResponse, summary="마이페이지 조회")
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.patch("/me", response_model=UserResponse, summary="회원 정보 수정")
async def update_me(
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> User:
    return await service.update_me(current_user, request)


@router.patch("/me/password", response_model=MessageResponse, summary="비밀번호 변경")
async def change_password(
    request: UserPasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> MessageResponse:
    await service.change_password(current_user, request)
    return MessageResponse(message="비밀번호가 변경되었습니다.")


@router.delete("/me", response_model=MessageResponse, summary="회원 탈퇴")
async def delete_me(
    response: Response,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> MessageResponse:
    await service.delete_me(current_user)
    response.delete_cookie("refresh_token")
    return MessageResponse(message="회원 탈퇴가 완료되었습니다.")

