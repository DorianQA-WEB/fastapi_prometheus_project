from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from prometheus_client import Counter, generate_latest, Gauge, Histogram
from pydantic import BaseModel
import time

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

# Модель для POST-запроса
class UserCreate(BaseModel):
    username: str


@app.get("/users/")
async def get_users():
    ACTIVE_CONNECTIONS.labels(app="fastapi").inc()
    start_time = time.time()
    try:
        REQUESTS_TOTAL.labels(method="GET", endpoint="/users/", status_code=200).inc()
        REQUEST_DURATION.labels(method="GET", endpoint="/users/").observe(time.time() - start_time)
        return {"message": "List of users"}
    finally:
        ACTIVE_CONNECTIONS.labels(app="fastapi").dec()


@app.post("/users/", status_code=201)
async def create_user(user: UserCreate, request: Request):
    ACTIVE_CONNECTIONS.labels(app="fastapi").inc()
    start_time = time.time()
    try:
        if len(user.username) < 3:
            REQUESTS_TOTAL.labels(method="POST", endpoint="/users/", status_code=400).inc()
            REQUEST_DURATION.labels(method="POST", endpoint="/users/").observe(time.time() - start_time)
            raise HTTPException(status_code=400, detail="Username is too short")
        REQUESTS_TOTAL.labels(method="POST", endpoint="/users/", status_code=201).inc()
        REQUEST_DURATION.labels(method="POST", endpoint="/users/").observe(time.time() - start_time)
        return {"message": "User created", "username": user.username}
    finally:
        ACTIVE_CONNECTIONS.labels(app="fastapi").dec()

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )
