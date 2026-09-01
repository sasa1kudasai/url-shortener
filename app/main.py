from fastapi import FastAPI

from app.routers import pages, shorten, auth

app = FastAPI()

app.include_router(pages.router)
app.include_router(shorten.router)
app.include_router(pages.router)
app.include_router(auth.router)