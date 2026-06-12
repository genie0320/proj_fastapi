# 4일차 - User API 설계

## 1. 설계 개요

사용자 관리는 회원가입, 로그인, 로그아웃, 마이페이지, 회원 정보 수정, 비밀번호 변경, 회원 탈퇴, 관리자 회원 목록 조회, 관리자 권한 변경 기능을 제공합니다.

### 공통 정책

| 항목 | 정책 |
|------|------|
| Base URL | `/api/v1/users` |
| 인증 방식 | Bearer Access Token |
| Access Token 만료 | 30분 |
| Refresh Token 만료 | 7일 |
| Refresh Token 저장 | `HttpOnly` 쿠키 |
| 기본 회원 권한 | `대기자` |
| 관리자 권한 | `어드민` |
| 탈퇴 방식 | 즉시 삭제(Hard Delete) |

### User 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| id | integer | 사용자 ID |
| email | string | 로그인 이메일, 중복 불가 |
| password | string | 해시 저장 대상 |
| name | string | 사용자 이름 |
| department | enum | `연구`, `의료`, `개발` |
| gender | enum | `M`, `F` |
| phone | string | 휴대폰 번호 |
| role | enum | `대기자`, `스태프`, `어드민` |
| created_at | datetime | 생성 일시 |
| updated_at | datetime | 수정 일시 |

## 2. API 명세

### REQ-USER-001 회원가입

| 항목 | 내용 |
|------|------|
| Method | `POST` |
| Endpoint | `/api/v1/users/signup` |
| 인증 | 불필요 |
| 설명 | 신규 사용자를 생성합니다. 생성된 사용자의 기본 권한은 `대기자`입니다. |

#### Request Body

```json
{
  "email": "doctor@example.com",
  "password": "Password123!",
  "name": "홍길동",
  "department": "의료",
  "gender": "M",
  "phone": "010-1234-5678"
}
```

#### Response `201 Created`

```json
{
  "id": 1,
  "email": "doctor@example.com",
  "name": "홍길동",
  "department": "의료",
  "gender": "M",
  "phone": "010-1234-5678",
  "role": "대기자",
  "created_at": "2026-06-07T03:00:00",
  "updated_at": "2026-06-07T03:00:00"
}
```

#### Error

| Status | 상황 |
|--------|------|
| 400 | 이미 사용 중인 이메일 |
| 422 | 요청값 검증 실패 |

### REQ-USER-002 로그인

| 항목 | 내용 |
|------|------|
| Method | `POST` |
| Endpoint | `/api/v1/users/login` |
| 인증 | 불필요 |
| 설명 | 이메일과 비밀번호를 검증하고 Access Token을 반환합니다. Refresh Token은 HttpOnly 쿠키에 저장합니다. |

#### Request Body

```json
{
  "email": "doctor@example.com",
  "password": "Password123!"
}
```

#### Response `200 OK`

```json
{
  "access_token": "jwt-access-token",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "doctor@example.com",
    "name": "홍길동",
    "department": "의료",
    "gender": "M",
    "phone": "010-1234-5678",
    "role": "대기자",
    "created_at": "2026-06-07T03:00:00",
    "updated_at": "2026-06-07T03:00:00"
  }
}
```

#### Error

| Status | 상황 |
|--------|------|
| 401 | 이메일 또는 비밀번호 불일치 |

### REQ-USER-003 로그아웃

| 항목 | 내용 |
|------|------|
| Method | `POST` |
| Endpoint | `/api/v1/users/logout` |
| 인증 | 필요 |
| 설명 | Refresh Token 쿠키를 삭제합니다. |

#### Response `200 OK`

```json
{
  "message": "로그아웃되었습니다."
}
```

### REQ-USER-004 회원 목록 조회(Admin)

| 항목 | 내용 |
|------|------|
| Method | `GET` |
| Endpoint | `/api/v1/users` |
| 인증 | 관리자 필요 |
| 설명 | 전체 회원 목록을 조회합니다. |

#### Query Parameters

| 이름 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| skip | integer | 0 | 건너뛸 개수 |
| limit | integer | 20 | 조회 개수 |

#### Response `200 OK`

```json
[
  {
    "id": 1,
    "email": "doctor@example.com",
    "name": "홍길동",
    "department": "의료",
    "gender": "M",
    "phone": "010-1234-5678",
    "role": "대기자",
    "created_at": "2026-06-07T03:00:00",
    "updated_at": "2026-06-07T03:00:00"
  }
]
```

#### Error

| Status | 상황 |
|--------|------|
| 401 | 인증 실패 |
| 403 | 관리자 권한 없음 |

### REQ-USER-005 회원 권한 변경(Admin)

| 항목 | 내용 |
|------|------|
| Method | `PATCH` |
| Endpoint | `/api/v1/users/{user_id}/role` |
| 인증 | 관리자 필요 |
| 설명 | 특정 회원의 권한을 변경합니다. |

#### Request Body

```json
{
  "role": "스태프"
}
```

#### Response `200 OK`

사용자 응답 객체를 반환합니다.

#### Error

| Status | 상황 |
|--------|------|
| 401 | 인증 실패 |
| 403 | 관리자 권한 없음 |
| 404 | 사용자를 찾을 수 없음 |

### REQ-USER-006 마이페이지 조회

| 항목 | 내용 |
|------|------|
| Method | `GET` |
| Endpoint | `/api/v1/users/me` |
| 인증 | 필요 |
| 설명 | 현재 로그인한 사용자의 정보를 조회합니다. |

#### Response `200 OK`

사용자 응답 객체를 반환합니다.

### REQ-USER-007 회원 정보 수정

| 항목 | 내용 |
|------|------|
| Method | `PATCH` |
| Endpoint | `/api/v1/users/me` |
| 인증 | 필요 |
| 설명 | 부서와 휴대폰 번호만 부분 수정합니다. |

#### Request Body

```json
{
  "department": "연구",
  "phone": "010-2222-3333"
}
```

#### Response `200 OK`

사용자 응답 객체를 반환합니다.

#### Error

| Status | 상황 |
|--------|------|
| 400 | 수정할 항목 없음 |
| 401 | 인증 실패 |

### REQ-USER-008 비밀번호 변경

| 항목 | 내용 |
|------|------|
| Method | `PATCH` |
| Endpoint | `/api/v1/users/me/password` |
| 인증 | 필요 |
| 설명 | 현재 비밀번호 확인 후 새 비밀번호로 변경합니다. |

#### Request Body

```json
{
  "current_password": "Password123!",
  "new_password": "NewPassword123!"
}
```

#### Response `200 OK`

```json
{
  "message": "비밀번호가 변경되었습니다."
}
```

#### Error

| Status | 상황 |
|--------|------|
| 400 | 현재 비밀번호 불일치 |
| 401 | 인증 실패 |

### REQ-USER-009 회원 탈퇴

| 항목 | 내용 |
|------|------|
| Method | `DELETE` |
| Endpoint | `/api/v1/users/me` |
| 인증 | 필요 |
| 설명 | 현재 로그인한 사용자를 즉시 삭제합니다. |

#### Response `200 OK`

```json
{
  "message": "회원 탈퇴가 완료되었습니다."
}
```

#### Error

| Status | 상황 |
|--------|------|
| 401 | 인증 실패 |
