from fastapi import HTTPException, status

from app.models.user import RoleEnum, User
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import (
    TokenResponse,
    UserLoginRequest,
    UserPasswordChangeRequest,
    UserResponse,
    UserSignupRequest,
    UserUpdateRequest,
)


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def signup(self, request: UserSignupRequest) -> User:
        if await self.repository.get_by_email(request.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 사용 중인 이메일입니다.")

        user = User(
            email=request.email,
            password=hash_password(request.password),
            name=request.name,
            department=request.department,
            gender=request.gender,
            phone=request.phone,
            role=RoleEnum.PENDING,
        )
        return await self.repository.create(user)

    async def login(self, request: UserLoginRequest) -> tuple[TokenResponse, str]:
        user = await self.repository.get_by_email(request.email)
        if user is None or not verify_password(request.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        response = TokenResponse(access_token=access_token, user=UserResponse.model_validate(user))
        return response, refresh_token

    async def list_users(self, skip: int, limit: int) -> list[User]:
        return await self.repository.list_users(skip=skip, limit=limit)

    async def get_user_or_404(self, user_id: int) -> User:
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다.")
        return user

    async def update_me(self, user: User, request: UserUpdateRequest) -> User:
        update_data = request.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="수정할 항목을 1개 이상 입력해주세요.")

        for key, value in update_data.items():
            setattr(user, key, value)
        return await self.repository.update(user)

    async def change_password(self, user: User, request: UserPasswordChangeRequest) -> None:
        if not verify_password(request.current_password, user.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="현재 비밀번호가 올바르지 않습니다.")
        user.password = hash_password(request.new_password)
        await self.repository.update(user)

    async def update_role(self, user_id: int, role: RoleEnum) -> User:
        user = await self.get_user_or_404(user_id)
        return await self.repository.update_role(user, role)

    async def delete_me(self, user: User) -> None:
        await self.repository.delete_by_id(user.id)

