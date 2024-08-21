"""Main module for miniapp API"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from miniapp_api import helpers
from miniapp_api.routers import users, teams, reactions, likes, admin, avatars, soft_skills

app = FastAPI()
app.include_router(users.router)
app.include_router(reactions.router)
app.include_router(teams.router)
app.include_router(likes.router)
app.include_router(admin.router)
app.include_router(avatars.router)
app.include_router(soft_skills.router)

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(helpers.APIException)
async def unicorn_exception_handler(
    _request: Request,
    exc: helpers.APIException
):
    """Custom API exceptions handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "ok": False,
            "error": exc.error
        },
    )
