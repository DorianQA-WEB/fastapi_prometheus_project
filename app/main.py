from fastapi import FastAPI, Request, HTTPException, Depends
from typing import List
from fastapi.responses import Response
from prometheus_client import Counter, generate_latest, Gauge, Histogram
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Column, Integer, String, Float, create_engine, select
from sqlalchemy.orm import Session, DeclarativeBase, sessionmaker
import time
import os

# -------------------- Pydantic-схемы --------------------
# Модель входных данных.
# Модель для POST-запроса
class UserCreate(BaseModel):
    username: str

class UserResponse(BaseModel):
    username: str
    id: int


# Модель входных данных
class ItemCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    price: float = Field(ge=0)



# Модель ответа клиенту.
class ItemResponse(BaseModel):
    id: int = Field(..., description="ID товара")
    name: str
    price: float
    model_config = ConfigDict(from_attributes=True)


# -------------------- SQLAlchemy-модели -----------------
class Base(DeclarativeBase):
    pass

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)

# -------------------- Настройка БД ----------------------
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./default.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Создаём схему при старте.
Base.metadata.create_all(bind=engine)

# -------------------- DI: выдача сессии -----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


# Метрика для подсчёта запросов
REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"]
)

ACTIVE_CONNECTIONS = Gauge(
    "active_connections",
    "Current number of active connections",
    ["app"]
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.1, 0.3, 0.5, 1.0, 2.0, 5.0]
)

@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.post("/items/", response_model=ItemResponse)
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item(name=item.name, price=item.price)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get("/users/", response_model=List[UserResponse], status_code=200)
async def get_users(db: Session = Depends(get_db)):
    ACTIVE_CONNECTIONS.labels(app="fastapi").inc()
    start_time = time.time()
    try:
        REQUESTS_TOTAL.labels(method="GET", endpoint="/users/", status_code=200).inc()
        REQUEST_DURATION.labels(method="GET", endpoint="/users/").observe(time.time() - start_time)
        result = db.scalars(select(User)).all()
        return result
    finally:
        ACTIVE_CONNECTIONS.labels(app="fastapi").dec()


@app.post("/users/", status_code=201, response_model=UserResponse)
async def create_user(user: UserCreate,
                      request: Request,
                      db: Session = Depends(get_db)):
    ACTIVE_CONNECTIONS.labels(app="fastapi").inc()
    start_time = time.time()
    try:
        if len(user.username) < 3:
            REQUESTS_TOTAL.labels(method="POST", endpoint="/users/", status_code=400).inc()
            REQUEST_DURATION.labels(method="POST", endpoint="/users/").observe(time.time() - start_time)
            raise HTTPException(status_code=400, detail="Username is too short")
        REQUESTS_TOTAL.labels(method="POST", endpoint="/users/", status_code=201).inc()
        REQUEST_DURATION.labels(method="POST", endpoint="/users/").observe(time.time() - start_time)
        result = db.scalars(select(User).where(User.username == user.username))
        if result.first():
            raise HTTPException(status_code=400, detail="Username already exists")
        db_user = User(username=user.username)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    finally:
        ACTIVE_CONNECTIONS.labels(app="fastapi").dec()

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )
