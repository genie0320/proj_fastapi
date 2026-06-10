# app/main.py
from fastapi import FastAPI
from app.apis.practice_apis import router as practice_router

app = FastAPI(
    title="AH Health Web Development Assignment",
    description="Practice CRUD API Sandbox",
    version="1.0.0",
)

# 생성한 라우터를 메인 앱에 탑재
app.include_router(practice_router)


@app.get("/")
def read_root():
    return {"message": "Server is running successfully."}
