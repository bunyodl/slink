from fastapi import FastAPI

from app.routers import health, links, redirect

app = FastAPI(title="Slink")

app.include_router(health.router)
app.include_router(links.router, prefix="/api")
app.include_router(redirect.router)
