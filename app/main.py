# app/main.py
from fastapi import FastAPI
from app.apis.practice_apis import router as practice_router
from app.apis.patient import router as patient_router
from app.apis.user_router import router as user_router

app = FastAPI(
    title="AH Health Web Development Assignment",
    description="Practice CRUD API Sandbox",
    version="1.0.0",
)

# 생성한 라우터들을 메인 앱에 탑재
app.include_router(practice_router)
app.include_router(patient_router)
app.include_router(user_router)


@app.get("/")
def read_root():
    return {"status": "healthy", "message": "All routers integrated successfully."}
