from sqlalchemy.orm import Session
import models
import schemas
from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import List

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def create_task(db: Session, task: schemas.TaskCreate, user_id: int):
    db_task = models.Task(**task.dict(), user_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# def get_tasks_by_date(db: Session, user_id: int, date: datetime):
#     # 获取指定日期的所有任务
#     start_of_day = datetime(date.year, date.month, date.day, 0, 0, 0)
#     end_of_day = start_of_day + timedelta(days=1)
    
#     return db.query(models.Task).filter(
#         models.Task.user_id == user_id,
#         models.Task.start >= start_of_day,
#         models.Task.start < end_of_day
#     ).all()

# 2026/06/30 16:33
# def get_tasks_by_date_range(db: Session, user_id: int, start: datetime, end: datetime):
#     return db.query(models.Task).filter(
#         models.Task.user_id == user_id,
#         models.Task.start >= start,
#         models.Task.start < end
#     ).all()

#2025年7月1日15:15
def get_tasks_by_date_range(db: Session, user_id: int, start: datetime, end: datetime):
    # 添加日志输出
    print(f"查询任务: user_id={user_id}, start={start}, end={end}")
    
    tasks = db.query(models.Task).filter(
        models.Task.user_id == user_id,
        models.Task.start >= start,
        models.Task.start < end
    ).all()
    
    print(f"找到 {len(tasks)} 个任务")
    return tasks

def get_tasks_by_id(db: Session, user_id: int):
    # 添加日志输出
    print(f"查询任务: user_id={user_id}")

    tasks = db.query(models.Task).filter(
        models.Task.user_id == user_id
        ).all()
    
    print(f"找到{len(tasks)}個任務")
    return tasks

def delete_task(db: Session, task_id: int, user_id: int):
    db_task = db.query(models.Task).filter(
        models.Task.id == task_id, 
        models.Task.user_id == user_id
    ).first()
    
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False

def create_memo(db: Session, memo: schemas.MemoCreate, user_id: int):
    db_memo = models.Memo(**memo.dict(), user_id=user_id)
    db.add(db_memo)
    db.commit()
    db.refresh(db_memo)
    return db_memo

def get_user_memos(db: Session, user_id: int):
    return db.query(models.Memo).filter(models.Memo.user_id == user_id).all()

def delete_memos(db: Session, memo_ids: List[int], user_id: int):
    result = db.query(models.Memo).filter(
        models.Memo.id.in_(memo_ids),
        models.Memo.user_id == user_id
    ).delete(synchronize_session=False)
    db.commit()
    return result

def update_memo(db: Session, memo_id: int, memo: schemas.MemoCreate, user_id: int):
    db_memo = db.query(models.Memo).filter(
        models.Memo.id == memo_id,
        models.Memo.user_id == user_id
    ).first()
    
    if db_memo:
        for key, value in memo.dict().items():
            setattr(db_memo, key, value)
        db.commit()
        db.refresh(db_memo)
        return db_memo
    return None