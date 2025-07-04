from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

import crud
import models
import schemas
import auth
from database import SessionLocal, engine
from config import settings

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# 在创建FastAPI app后添加以下代码
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 生产环境应该更严格
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 用户认证
@app.post("/api/auth/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.post("/api/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 2025/06/29 16:05
@app.post("/api/auth/logout")
def logout(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    # 将token加入黑名单
    auth.token_blacklist.add(token)
    return {"message": "Successfully logged out"}

@app.get("/api/auth/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user

# 待办事项API
@app.post("/api/tasks", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db), 
               current_user: schemas.User = Depends(auth.get_current_user)):
    return crud.create_task(db=db, task=task, user_id=current_user.id)

# 2026/06/30 16:33
@app.get("/api/home/tasks", response_model=List[schemas.Task])
def get_tasks(start: datetime, end: datetime = None, db: Session = Depends(get_db), 
             current_user: schemas.User = Depends(auth.get_current_user)):
    # 如果没有提供end参数，默认为start的同一天结束
    if end is None:
        end = start + timedelta(days=1)
    return crud.get_tasks_by_date_range(db, user_id=current_user.id, start=start, end=end)

@app.get("/api/tasks", response_model=List[schemas.Task])
def get_tasks(db: Session = Depends(get_db), 
            current_user: schemas.User = Depends(auth.get_current_user)):
    
    return crud.get_tasks_by_id(db, user_id = current_user.id)

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), 
               current_user: schemas.User = Depends(auth.get_current_user)):
    if not crud.delete_task(db, task_id=task_id, user_id=current_user.id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}

# 备忘录API
@app.post("/api/memos", response_model=schemas.Memo)
def create_memo(memo: schemas.MemoCreate, db: Session = Depends(get_db), 
               current_user: schemas.User = Depends(auth.get_current_user)):
    return crud.create_memo(db=db, memo=memo, user_id=current_user.id)

@app.get("/api/memos", response_model=List[schemas.Memo])
def get_memos(db: Session = Depends(get_db), 
             current_user: schemas.User = Depends(auth.get_current_user)):
    return crud.get_user_memos(db, user_id=current_user.id)

@app.delete("/api/memos")
def delete_memos(
    memo_ids: List[int] = Body(..., embed=True, alias="memo_ids"),
    db: Session = Depends(get_db), 
    current_user: schemas.User = Depends(auth.get_current_user)):
    if not memo_ids:
        raise HTTPException(status_code=400, detail="No memo IDs provided")
    result = crud.delete_memos(db, memo_ids=memo_ids, user_id=current_user.id)
    if result == 0:
        raise HTTPException(status_code=404, detail="No memos found or some memos don't belong to the user")
    return {"message": f"{result} memos deleted"}

@app.put("/api/memos/{memo_id}", response_model=schemas.Memo)
def update_memo(memo_id: int, memo: schemas.MemoCreate, db: Session = Depends(get_db), 
               current_user: schemas.User = Depends(auth.get_current_user)):
    updated_memo = crud.update_memo(db, memo_id=memo_id, memo=memo, user_id=current_user.id)
    if updated_memo is None:
        raise HTTPException(status_code=404, detail="Memo not found")
    return updated_memo

# 健康检查
@app.get("/")
def read_root():
    return {"status": "OK", "message": "LifeCursor API is running"}