# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.apis.practice_apis import router as practice_router
from app.apis.patient import router as patient_router
from app.apis.user_router import router as user_router
from app.apis.record_router import router as record_router

app = FastAPI(
    title="AH Health Web Development Assignment",
    description="Practice CRUD API Sandbox",
    version="1.0.0",
)

# 생성한 라우터들을 메인 앱에 탑재
app.include_router(practice_router)
app.include_router(patient_router)
app.include_router(user_router)
app.include_router(record_router)

# 정적 파일 서빙 등록
app.mount("/static", StaticFiles(directory="static"), name="static")

# 미디어 파일 서빙 등록 (필요시)
import os
if os.path.exists("media"):
    app.mount("/media", StaticFiles(directory="media"), name="media")


# SPA 페이지 라우트 매핑
@app.get("/")
@app.get("/login")
@app.get("/signup")
@app.get("/patients")
@app.get("/patients/create")
@app.get("/patients/{patient_id}")
@app.get("/patients/{patient_id}/medical-records/create")
@app.get("/medical-records/{record_id}")
@app.get("/my-page")
@app.get("/admin/users")
async def serve_spa():
    return FileResponse("static/index.html")


@app.get("/healthcheck", status_code=200, include_in_schema=False)
async def healthcheck():
    return {"status": "healthy"}

