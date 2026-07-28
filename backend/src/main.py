from fastapi import FastAPI

from modules.tickets.api.api import router as tickets_router

app = FastAPI()
app.include_router(tickets_router)
