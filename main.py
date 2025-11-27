from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from database import init_db
from routers import operators, sources, contacts, leads, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    pass


app = FastAPI(
    title="Мини-CRM распределения лидов",
    description="Сервис автоматического распределения обращений лидов между операторами",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(operators.router)
app.include_router(sources.router)
app.include_router(contacts.router)
app.include_router(leads.router)
app.include_router(stats.router)


@app.get("/")
async def root():
    return {
        "message": "Мини-CRM распределения лидов",
        "docs": "/docs",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

