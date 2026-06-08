import base64
import hashlib
import hmac
import json
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status

from app.core.config import settings


ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
_SECRET_KEY = f"{settings.DB_PASSWORD}:{settings.DB_NAME}".encode()


def validate_password_rule(password: str) -> str:
    if not (8 <= len(password) <= 20):
        raise ValueError("비밀번호는 8자 이상 20자 이하여야 합니다.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("비밀번호에 대문자가 1개 이상 포함되어야 합니다.")
    if not re.search(r"[a-z]", password):
        raise ValueError("비밀번호에 소문자가 1개 이상 포함되어야 합니다.")
    if not re.search(r"[0-9]", password):
        raise ValueError("비밀번호에 숫자가 1개 이상 포함되어야 합니다.")
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        raise ValueError("비밀번호에 특수문자가 1개 이상 포함되어야 합니다.")
    return password


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120_000)
    return f"pbkdf2_sha256${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        algorithm, salt_text, digest_text = hashed_password.split("$")
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False

    salt = base64.urlsafe_b64decode(salt_text.encode())
    saved_digest = base64.urlsafe_b64decode(digest_text.encode())
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120_000)
    return hmac.compare_digest(digest, saved_digest)


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _base64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode())


def create_token(subject: str, expires_delta: timedelta, token_type: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    header = {"alg": "HS256", "typ": "JWT"}
    header_text = _base64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_text = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signature = hmac.new(_SECRET_KEY, f"{header_text}.{payload_text}".encode(), hashlib.sha256).digest()
    return f"{header_text}.{payload_text}.{_base64url_encode(signature)}"


def create_access_token(user_id: int) -> str:
    return create_token(str(user_id), timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), "access")


def create_refresh_token(user_id: int) -> str:
    return create_token(str(user_id), timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), "refresh")


def decode_token(token: str, expected_type: str = "access") -> dict[str, Any]:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 유효하지 않습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        header_text, payload_text, signature_text = token.split(".")
        expected_signature = hmac.new(
            _SECRET_KEY,
            f"{header_text}.{payload_text}".encode(),
            hashlib.sha256,
        ).digest()
        actual_signature = _base64url_decode(signature_text)
        if not hmac.compare_digest(expected_signature, actual_signature):
            raise credentials_error

        payload = json.loads(_base64url_decode(payload_text))
        if payload.get("type") != expected_type:
            raise credentials_error
        if datetime.now(timezone.utc).timestamp() > payload.get("exp", 0):
            raise credentials_error
        return payload
    except (ValueError, json.JSONDecodeError, TypeError):
        raise credentials_error

