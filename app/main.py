from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import Counter, generate_latest

app = FastAPI()

# Метрика для подсчёта запросов
REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"]
)


@app.get("/users/")
async def get_users():
    REQUESTS_TOTAL.labels(method="GET", endpoint="/users/", status_code=200).inc()
    return {"message": "List of users"}

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )
