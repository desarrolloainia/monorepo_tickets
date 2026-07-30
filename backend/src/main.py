from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modules.auth.router import router as auth_router
from modules.tickets.api.api import router as tickets_router
from modules.users.api.api import router as users_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tickets_router)
