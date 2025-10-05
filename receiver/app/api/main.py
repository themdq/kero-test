from fastapi import APIRouter

from app.api.routes import events

api_router = APIRouter()
api_router.include_router(events.router)
